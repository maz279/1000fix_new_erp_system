# M19 Financial Accounting & GL: capture audit, second pass (19 Nov 2026).
#
# The user again saw M19 sub-module pages without a relevant capture. Two pages
# still offered no "+ New" at all, and the spec records behind three more had
# no model:
#   3  Subledger Posting Engine   no posting rules (FR-FIN-008/009/010,
#                                 BRU-FIN-17/18): nothing to capture
#   8  Audit & Retention          no external auditor access (FR-FIN-043,
#                                 BRU-FIN-26): nothing to capture
#   1  CoA & Dimensions           no cross-validation rules (FR-FIN-004,
#                                 BRU-FIN-22, a hard block)
#   4  Fiscal Calendar & Close    no fiscal year capture, and no July-June rule
#                                 (FR-FIN-018, BRU-FIN-19)
#   6  Multi-Currency             no exchange-rate capture (FR-FIN-033): the FX
#                                 revaluation refuses to run without the
#                                 official rate, and no screen could enter one
# Every save runs through the workspace endpoints (/p03/model/write and
# /p03/model/action) as a non-admin user holding only finance roles.
from __future__ import annotations

from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.addons.cd_gl_ext.models.fix_gl_ext import (
    create_journal_entry_draft,
    post_with_dimensions,
)
from odoo.addons.cd_gl_ext.tests.test_a08_m19_operability import (  # noqa: F401
    ACC_MGR,
    ACC_USER,
    BILL,
    _user,
    c,
    p03,
    whitelist,
)
from odoo.addons.cd_p03_portal.controllers.a08 import m19 as m19_surfaces
from odoo.addons.cd_p03_portal.controllers.a08.writable import WRITABLE
from odoo.addons.cd_p03_portal.tests.test_m19_capture_buttons import m19  # noqa: F401
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]
REFUSED = (UserError, ValidationError, AccessError)

PASS2 = {
    "1": (None, {"Cross-Validation Rule"}),
    "3": ("M19-form-posting-rule", {"Posting Rule"}),
    "4": (None, {"Fiscal Year (July–June)"}),
    "6": ("M19-form-fx-rate", {"Exchange Rate", "FX Revaluation Run"}),
    "8": ("M19-form-auditor-grant", {"External Auditor Access", "Retention Policy"}),
}
NEW_MODELS = (
    "fix.gl.crossvalidation.rule",
    "fix.gl.posting.rule",
    "account.fiscal.year",
    "fix.currency.rate.entry",
    "fix.auditor.access.grant",
)


# --------------------------------------------------------------- the pages
@pytest.mark.parametrize("no", sorted(PASS2, key=int))
def test_each_page_offers_the_record_the_spec_names(m19, no):  # noqa: F811
    sub = next(s for s in m19["subs"] if s["no"] == no)
    screen, chips = PASS2[no]
    assert sub["create"], "page %s has no + New" % no
    if screen:
        assert sub["create"]["screen"] == screen, sub["create"]
    named = {f["f"] for f in sub["forms"] if f["opens"]}
    assert chips <= named, named


def test_every_new_register_is_served_with_its_workflow_actions():
    for model in NEW_MODELS:
        assert model in m19_surfaces.SURFACES, model
        assert WRITABLE.get(model), model
    acts = m19_surfaces.SURFACES
    assert {"action_run_tests", "action_approve", "action_new_version"} <= acts[
        "fix.gl.posting.rule"
    ]["actions"]
    assert {"action_grant", "action_revoke"} <= acts["fix.auditor.access.grant"]["actions"]
    assert {"action_submit", "action_approve"} <= acts["fix.currency.rate.entry"]["actions"]
    # workflow fields are never typed
    for model, banned in (
        ("fix.gl.posting.rule", {"state", "version", "approved_by_id"}),
        ("fix.currency.rate.entry", {"state", "approved_by_id", "published_rate_id"}),
        ("fix.auditor.access.grant", {"state", "granted_by_id"}),
        ("fix.gl.crossvalidation.rule", {"state", "activated_by_id"}),
    ):
        assert not banned & WRITABLE[model], (model, banned & WRITABLE[model])


# --------------------------------------------------------------- helpers
def _acc(c, code, kind="expense"):  # noqa: F811 - the fixture object
    return (
        c.env["account.account"]
        .with_company(c.co)
        .create(
            {"code": code, "name": code, "account_type": kind, "company_ids": [(6, 0, c.co.ids)]}
        )
    )


def _move_vals(c, dr, cr, amount=100.0, day=None):  # noqa: F811 - the fixture object
    return {
        "journal_id": c.misc.id,
        "date": day or c.today,
        "ref": "M19 pass 2",
        "line_ids": [
            (0, 0, {"name": "dr", "account_id": dr.id, "debit": amount}),
            (0, 0, {"name": "cr", "account_id": cr.id, "credit": amount}),
        ],
    }


def _ok(out):
    assert out and not out.get("error"), out
    return out


def _act(p03, user, model, rec, method, **kwargs):  # noqa: F811
    p03.as_user(user)
    return p03.action(model=model, ids=rec.ids, method=method, kwargs=kwargs or {})


# --------------------------------------------------------------- page 1
def test_a_deny_rule_refuses_the_combination_on_every_posting_path(c, p03):  # noqa: F811
    rent, cash = _acc(c, "M19XR01", "income"), _acc(c, "M19XC01", "asset_cash")
    p03.as_user(c.acct)
    out = _ok(
        p03.write(
            model="fix.gl.crossvalidation.rule",
            values={
                "name": "Rental revenue never carries the repair line",
                "account_prefix": "M19XR",
                "dimension": "business_line",
                "effect": "deny",
                "values": "Repair, Field Repair",
            },
        )
    )
    rule = c.env["fix.gl.crossvalidation.rule"].browse(out["id"])
    # the author cannot activate; a plain accountant cannot at all
    res = _act(p03, c.acct, rule._name, rule, "action_activate")
    assert not res.get("success"), res
    _ok_act = _act(p03, c.mgr, rule._name, rule, "action_activate")
    assert _ok_act.get("success"), _ok_act
    assert rule.state == "active" and rule.activated_by_id == c.mgr

    bad = {0: {"business_line": "repair"}, 1: {"business_line": "repair"}}
    with pytest.raises(UserError, match="cross-validation"):
        post_with_dimensions(c.env, _move_vals(c, cash, rent), bad, source="api")
    with pytest.raises(UserError, match="cross-validation"):
        create_journal_entry_draft(c.env(user=c.acct.id), _move_vals(c, cash, rent), bad)
    good = {0: {"business_line": "Rental"}, 1: {"business_line": "Rental"}}
    move, _dims = post_with_dimensions(c.env, _move_vals(c, cash, rent), good, source="api")
    assert move.state == "posted"


def test_an_allow_only_rule_demands_a_listed_value(c, p03):  # noqa: F811
    exp, cash = _acc(c, "M19XE01"), _acc(c, "M19XC02", "asset_cash")
    rule = (
        c.env["fix.gl.crossvalidation.rule"]
        .with_user(c.acct)
        .create(
            {
                "name": "Workshop costs carry a workshop cost centre",
                "account_prefix": "M19XE",
                "dimension": "cost_centre",
                "effect": "allow_only",
                "values": "CC-WS1,CC-WS2",
            }
        )
    )
    rule.with_user(c.mgr).action_activate()
    with pytest.raises(UserError, match="must carry"):
        post_with_dimensions(c.env, _move_vals(c, exp, cash), {}, source="api")
    move, _d = post_with_dimensions(
        c.env, _move_vals(c, exp, cash), {0: {"cost_centre": "cc-ws2"}}, source="api"
    )
    assert move.state == "posted"


def test_an_active_rule_is_never_edited_and_a_retired_one_stops(c, p03):  # noqa: F811
    rent, cash = _acc(c, "M19XR02", "income"), _acc(c, "M19XC03", "asset_cash")
    rule = (
        c.env["fix.gl.crossvalidation.rule"]
        .with_user(c.acct)
        .create(
            {
                "name": "No Samsung on rental",
                "account_prefix": "M19XR02",
                "dimension": "brand",
                "effect": "deny",
                "values": "Samsung",
            }
        )
    )
    rule.with_user(c.mgr).action_activate()
    p03.as_user(c.acct)
    out = p03.write(model=rule._name, record_id=rule.id, values={"values": "Walton"})
    assert out.get("error")
    with pytest.raises(UserError):
        rule.with_user(c.mgr).write({"values": "Walton"})
    with pytest.raises(UserError):
        rule.with_user(c.acct).write({"state": "retired"})
    rule.with_user(c.mgr).action_retire()
    move, _d = post_with_dimensions(
        c.env, _move_vals(c, cash, rent), {1: {"brand": "Samsung"}}, source="api"
    )
    assert move.state == "posted"


# --------------------------------------------------------------- page 3
def _posting_rule(c, p03, dr, cr, *, amount=1000.0, exp_dr=None, effective=None):  # noqa: F811
    p03.as_user(c.acct)
    out = _ok(
        p03.write(
            model="fix.gl.posting.rule",
            values={
                "name": "API costs: expense against cash",
                "source": "api",
                "effective_from": str(effective or c.today - timedelta(days=30)),
            },
            lines={
                "field": "line_ids",
                "rows": [
                    {"values": {"side": "debit", "account_id": dr.id, "share_percent": 100}},
                    {"values": {"side": "credit", "account_id": cr.id, "share_percent": 100}},
                ],
            },
            grids=[
                {
                    "field": "fixture_ids",
                    "rows": [
                        {
                            "values": {
                                "sample_amount": amount,
                                "account_id": dr.id,
                                "expected_debit": exp_dr or amount,
                            }
                        },
                        {
                            "values": {
                                "sample_amount": amount,
                                "account_id": cr.id,
                                "expected_credit": amount,
                            }
                        },
                    ],
                }
            ],
        )
    )
    return c.env["fix.gl.posting.rule"].browse(out["id"])


def test_a_posting_rule_is_tested_then_approved_by_someone_else(c, p03):  # noqa: F811
    exp, cash = _acc(c, "M19PE01"), _acc(c, "M19PC01", "asset_cash")
    rule = _posting_rule(c, p03, exp, cash)
    assert rule.state == "draft" and rule.version >= 1 and len(rule.line_ids) == 2
    assert len(rule.fixture_ids) == 2
    res = _act(p03, c.mgr, rule._name, rule, "action_approve")
    assert not res.get("success"), "approved without passing fixtures"
    assert _act(p03, c.acct, rule._name, rule, "action_run_tests").get("success")
    assert rule.state == "tested", rule.last_test_result
    # never edited in place once tested
    p03.as_user(c.acct)
    assert p03.write(model=rule._name, record_id=rule.id, values={"name": "x"}).get("error")
    with pytest.raises(UserError):
        rule.line_ids[:1].with_user(c.acct).write({"share_percent": 50})
    with pytest.raises(UserError):
        rule.fixture_ids[:1].with_user(c.acct).unlink()
    # the author cannot approve; another accounting manager can
    rule.write({})  # noop
    assert not _act(p03, c.acct, rule._name, rule, "action_approve").get("success")
    assert _act(p03, c.mgr, rule._name, rule, "action_approve").get("success")
    assert rule.state == "active" and rule.approved_by_id == c.mgr


def test_a_failing_fixture_keeps_the_rule_in_draft(c, p03):  # noqa: F811
    exp, cash = _acc(c, "M19PE02"), _acc(c, "M19PC02", "asset_cash")
    rule = _posting_rule(c, p03, exp, cash, exp_dr=999.0)
    _act(p03, c.acct, rule._name, rule, "action_run_tests")
    assert rule.state == "draft" and "FAIL" in (rule.last_test_result or "")
    with pytest.raises(UserError):
        rule.with_user(c.mgr).action_approve()


def test_an_unbalanced_rule_cannot_be_tested(c, p03):  # noqa: F811
    exp, cash = _acc(c, "M19PE03"), _acc(c, "M19PC03", "asset_cash")
    rule = _posting_rule(c, p03, exp, cash)
    rule.line_ids.filtered(lambda line: line.side == "credit").write({"share_percent": 60})
    with pytest.raises(UserError, match="100%"):
        rule.with_user(c.acct).action_run_tests()


def test_the_rule_in_force_governs_its_sources_postings(c, p03):  # noqa: F811
    exp, cash, other = (
        _acc(c, "M19PE04"),
        _acc(c, "M19PC04", "asset_cash"),
        _acc(c, "M19PO04"),
    )
    rule = _posting_rule(c, p03, exp, cash)
    rule.with_user(c.acct).action_run_tests()
    rule.with_user(c.mgr).action_approve()
    move, _d = post_with_dimensions(c.env, _move_vals(c, exp, cash), {}, source="api")
    log = c.env["fix.journal.posting.log"].search([("move_id", "=", move.id)])
    assert log.posting_rule_id == rule, "FR-FIN-010: the entry names its rule version"
    with pytest.raises(UserError, match="does not post to"):
        post_with_dimensions(c.env, _move_vals(c, other, cash), {}, source="api")
    # another source is not governed by it
    move2, _d = post_with_dimensions(c.env, _move_vals(c, other, cash), {}, source="settlement")
    assert move2.state == "posted"


def test_a_new_version_supersedes_and_the_old_one_still_explains_old_dates(c, p03):  # noqa: F811
    exp, cash, exp2 = _acc(c, "M19PE05"), _acc(c, "M19PC05", "asset_cash"), _acc(c, "M19PF05")
    v1 = _posting_rule(c, p03, exp, cash, effective=c.today - timedelta(days=60))
    v1.with_user(c.acct).action_run_tests()
    v1.with_user(c.mgr).action_approve()
    res = _act(p03, c.acct, v1._name, v1, "action_new_version")
    assert res.get("success"), res
    v2 = c.env["fix.gl.posting.rule"].search(
        [("source", "=", "api"), ("company_id", "=", v1.company_id.id), ("state", "=", "draft")],
        order="version desc",
        limit=1,
    )
    assert v2.version == v1.version + 1 and v2.effective_from >= c.today
    # the copy is a draft: its lines change, then it is tested and approved
    v2.line_ids.filtered(lambda line: line.side == "debit").with_user(c.acct2).write(
        {"account_id": exp2.id}
    )
    v2.fixture_ids.filtered(lambda f: f.account_id == exp).with_user(c.acct2).write(
        {"account_id": exp2.id}
    )
    v2.with_user(c.acct2).action_run_tests()
    with pytest.raises(UserError):
        v2.with_user(c.acct2).action_approve()  # not a manager
    v2.with_user(c.mgr2).action_approve()
    assert v1.state == "superseded" and v2.state == "active" and v2.previous_version_id == v1
    old, _d = post_with_dimensions(
        c.env, _move_vals(c, exp, cash, day=c.today - timedelta(days=10)), {}, source="api"
    )
    assert c.env["fix.journal.posting.log"].search([("move_id", "=", old.id)]).posting_rule_id == v1
    with pytest.raises(UserError, match="does not post to"):
        post_with_dimensions(c.env, _move_vals(c, exp, cash), {}, source="api")
    with pytest.raises(UserError):
        v1.with_user(c.mgr).unlink()


def test_manual_journals_are_not_a_posting_rule_source(c):  # noqa: F811
    sources = dict(c.env["fix.gl.posting.rule"]._fields["source"]._description_selection(c.env))
    assert "manual" not in sources and "api" in sources


# --------------------------------------------------------------- page 4
def test_the_fiscal_year_runs_july_to_june(c, p03):  # noqa: F811
    p03.as_user(c.mgr)
    out = p03.write(
        model="account.fiscal.year",
        values={
            "name": "Calendar 2031",
            "date_from": "2031-01-01",
            "date_to": "2031-12-31",
            "company_id": c.co.id,
        },
    )
    assert out.get("error"), "a calendar-year fiscal year was accepted"
    out = _ok(
        p03.write(
            model="account.fiscal.year",
            values={
                "name": "FY2031-32",
                "date_from": "2031-07-01",
                "date_to": "2032-06-30",
                "company_id": c.co.id,
            },
        )
    )
    with pytest.raises(ValidationError):
        c.env["account.fiscal.year"].browse(out["id"]).write({"date_to": "2032-07-31"})


# --------------------------------------------------------------- page 6
def _rate(c, p03, user, **vals):  # noqa: F811
    p03.as_user(user)
    base = {
        "currency_id": c.env.ref("base.USD").id,
        "rate_type": "closing",
        "rate_date": str(c.today),
        "rate_bdt": 122.5,
        "source": "bangladesh_bank",
        "source_ref": "BB circular",
    }
    base.update(vals)
    out = p03.write(model="fix.currency.rate.entry", values=base)
    return out


def test_an_approved_closing_rate_becomes_the_ledger_rate(c, p03):  # noqa: F811
    usd = c.env.ref("base.USD")
    usd.sudo().active = True
    out = _ok(_rate(c, p03, c.acct))
    entry = c.env["fix.currency.rate.entry"].browse(out["id"])
    assert entry.company_id == c.co.root_id
    assert _act(p03, c.acct, entry._name, entry, "action_submit").get("success")
    # frozen once submitted
    p03.as_user(c.acct)
    assert p03.write(model=entry._name, record_id=entry.id, values={"rate_bdt": 1.0}).get("error")
    # the entrant cannot approve
    assert not _act(p03, c.acct, entry._name, entry, "action_approve").get("success")
    assert _act(p03, c.mgr, entry._name, entry, "action_approve").get("success")
    assert entry.state == "approved" and entry.published_rate_id
    rate = usd._get_conversion_rate(usd, c.co.currency_id, c.co, c.today)
    assert abs(rate - 122.5) < 1e-6, rate
    # the FX revaluation now finds the official closing rate
    run = c.env["fix.fx.revaluation"].new({"rate_date": c.today, "company_id": c.co.id})
    got, on = run._closing_rate(usd)
    assert abs(got - 122.5) < 1e-6 and on == c.today


def test_one_approved_rate_per_type_and_day_and_closing_beats_spot(c, p03):  # noqa: F811
    c.env.ref("base.USD").sudo().active = True
    first = c.env["fix.currency.rate.entry"].browse(_ok(_rate(c, p03, c.acct))["id"])
    first.with_user(c.acct).action_submit()
    first.with_user(c.mgr).action_approve()
    dup = c.env["fix.currency.rate.entry"].browse(_ok(_rate(c, p03, c.acct, rate_bdt=123.0))["id"])
    dup.with_user(c.acct).action_submit()
    with pytest.raises(UserError, match="already exists"):
        dup.with_user(c.mgr).action_approve()
    spot = c.env["fix.currency.rate.entry"].browse(
        _ok(_rate(c, p03, c.acct, rate_type="spot", rate_bdt=121.0))["id"]
    )
    spot.with_user(c.acct).action_submit()
    spot.with_user(c.mgr).action_approve()
    assert not spot.published_rate_id
    assert abs(first.published_rate_id.inverse_company_rate - 122.5) < 1e-6


def test_a_manual_override_states_why(c, p03):  # noqa: F811
    c.env.ref("base.USD").sudo().active = True
    out = _rate(c, p03, c.acct, source="manual")
    assert out.get("error"), "a manual override without a reason was accepted"
    _ok(_rate(c, p03, c.acct, source="manual", override_reason="Bank Bangladesh feed down"))
    assert _rate(c, p03, c.acct, rate_bdt=0).get("error")


# --------------------------------------------------------------- page 8
def _auditor(c, *groups):  # noqa: F811 - the fixture object
    return _user(c.env, "m19aud_%s" % len(groups), list(groups))


def _grant(c, p03, user, **vals):  # noqa: F811
    p03.as_user(c.acct)
    base = {
        "user_id": user.id,
        "engagement_ref": "EL-2026-07",
        "company_ids": [(6, 0, c.co.ids)],
        "period_from": str(c.today - timedelta(days=40)),
        "period_to": str(c.today - timedelta(days=20)),
        "valid_from": str(c.today),
        "valid_to": str(c.today + timedelta(days=30)),
    }
    base.update(vals)
    return p03.write(model="fix.auditor.access.grant", values=base)


def test_auditor_access_is_read_only_scoped_and_granted_by_someone_else(c, p03):  # noqa: F811
    aud = _auditor(c)
    exp, cash = _acc(c, "M19AE01"), _acc(c, "M19AC01", "asset_cash")
    inside, _d = post_with_dimensions(
        c.env, _move_vals(c, exp, cash, day=c.today - timedelta(days=30)), {}, source="api"
    )
    outside, _d = post_with_dimensions(
        c.env, _move_vals(c, exp, cash, day=c.today - timedelta(days=5)), {}, source="api"
    )
    out = _grant(c, p03, aud)
    grant = c.env["fix.auditor.access.grant"].browse(_ok(out)["id"])
    assert not _act(p03, c.acct, grant._name, grant, "action_grant").get("success")
    assert _act(p03, c.mgr, grant._name, grant, "action_grant").get("success")
    assert grant.state == "active" and aud.has_group("cd_gl_ext.group_external_auditor")
    assert aud.has_group("account.group_account_readonly")
    seen = (
        c.env(user=aud.id)["account.move.line"]
        .search([("account_id", "in", (exp | cash).ids)])
        .mapped("move_id")
    )
    assert inside in seen and outside not in seen, "BRU-FIN-26: scoped to the audited period"
    with pytest.raises(AccessError):
        inside.with_user(aud).write({"ref": "changed by the auditor"})
    # the grant is frozen once given
    p03.as_user(c.mgr)
    assert p03.write(
        model=grant._name,
        record_id=grant.id,
        values={"valid_to": str(c.today + timedelta(days=60))},
    ).get("error")
    assert _act(p03, c.mgr, grant._name, grant, "action_revoke").get("success")
    assert grant.state == "revoked" and not aud.has_group("cd_gl_ext.group_external_auditor")


def test_a_login_that_can_change_the_books_is_refused(c, p03):  # noqa: F811
    aud = _auditor(c, BILL)
    grant = c.env["fix.auditor.access.grant"].browse(_ok(_grant(c, p03, aud))["id"])
    with pytest.raises(UserError, match="read-only"):
        grant.with_user(c.mgr).action_grant()


def test_access_is_time_limited_and_lapses_by_itself(c, p03):  # noqa: F811
    aud = _auditor(c)
    assert _grant(c, p03, aud, valid_to=str(c.today + timedelta(days=200))).get("error")
    grant = c.env["fix.auditor.access.grant"].browse(_ok(_grant(c, p03, aud))["id"])
    grant.with_user(c.mgr).action_grant()
    grant.sudo().write(
        {"valid_from": c.today - timedelta(days=10), "valid_to": c.today - timedelta(days=1)}
    )
    assert c.env["fix.auditor.access.grant"]._cron_expire() >= 1
    assert grant.state == "expired" and not aud.has_group("cd_gl_ext.group_external_auditor")


def test_the_grant_cannot_reach_beyond_the_logins_companies(c, p03):  # noqa: F811
    aud = _auditor(c)
    other = c.env["res.company"].create({"name": "M19 other entity"})
    aud.sudo().write({"company_ids": [(4, other.id)]})
    grant = c.env["fix.auditor.access.grant"].browse(_ok(_grant(c, p03, aud))["id"])
    with pytest.raises(UserError, match="outside the grant"):
        grant.with_user(c.mgr).action_grant()


def test_the_window_is_a_parameter_and_dates_are_ordered(c, p03):  # noqa: F811
    aud = _auditor(c)
    assert _grant(
        c, p03, aud, period_from=str(c.today), period_to=str(c.today - relativedelta(days=1))
    ).get("error")
    c.env["ir.config_parameter"].sudo().set_param("cd_gl_ext.auditor_access_max_days", "200")
    _ok(_grant(c, p03, aud, valid_to=str(fields.Date.add(c.today, days=150))))


# --------------------------------------------------------------- makers never approve
# A maker who ALSO holds the approving role is the case segregation of duties
# exists for (the mutation check showed a non-manager maker proves nothing:
# the role check refuses them first).
def test_a_manager_never_approves_what_they_made(c, p03):  # noqa: F811
    c.env.ref("base.USD").sudo().active = True
    xv = (
        c.env["fix.gl.crossvalidation.rule"]
        .with_user(c.mgr)
        .create(
            {
                "name": "Self-activated",
                "account_prefix": "M19XS",
                "dimension": "channel",
                "effect": "deny",
                "values": "mail-in",
            }
        )
    )
    with pytest.raises(UserError, match="Segregation"):
        xv.with_user(c.mgr).action_activate()
    xv.with_user(c.mgr2).action_activate()

    exp, cash = _acc(c, "M19SE01"), _acc(c, "M19SC01", "asset_cash")
    rule = (
        c.env["fix.gl.posting.rule"]
        .with_user(c.mgr)
        .create(
            {
                "name": "Self-approved",
                "source": "settlement",
                "line_ids": [
                    (0, 0, {"side": "debit", "account_id": exp.id, "share_percent": 100}),
                    (0, 0, {"side": "credit", "account_id": cash.id, "share_percent": 100}),
                ],
                "fixture_ids": [
                    (0, 0, {"sample_amount": 10, "account_id": exp.id, "expected_debit": 10}),
                    (0, 0, {"sample_amount": 10, "account_id": cash.id, "expected_credit": 10}),
                ],
            }
        )
    )
    rule.with_user(c.mgr).action_run_tests()
    with pytest.raises(UserError, match="Segregation"):
        rule.with_user(c.mgr).action_approve()
    rule.with_user(c.mgr2).action_approve()

    entry = c.env["fix.currency.rate.entry"].browse(_ok(_rate(c, p03, c.mgr))["id"])
    entry.with_user(c.mgr).action_submit()
    with pytest.raises(UserError, match="Segregation"):
        entry.with_user(c.mgr).action_approve()
    entry.with_user(c.mgr2).action_approve()

    aud = _auditor(c)
    p03.as_user(c.mgr)
    grant = c.env["fix.auditor.access.grant"].browse(
        _ok(
            p03.write(
                model="fix.auditor.access.grant",
                values={
                    "user_id": aud.id,
                    "engagement_ref": "EL-SELF",
                    "company_ids": [(6, 0, c.co.ids)],
                    "period_from": str(c.today - timedelta(days=40)),
                    "period_to": str(c.today - timedelta(days=20)),
                    "valid_to": str(c.today + timedelta(days=10)),
                },
            )
        )["id"]
    )
    with pytest.raises(UserError, match="Segregation"):
        grant.with_user(c.mgr).action_grant()
    grant.with_user(c.mgr2).action_grant()
    assert grant.state == "active"

    # frozen at the model, not only on the form
    with pytest.raises(UserError, match="frozen"):
        entry.with_user(c.mgr2).write({"rate_bdt": 1.0})
    with pytest.raises(UserError, match="frozen"):
        grant.with_user(c.mgr2).write({"valid_to": c.today + timedelta(days=20)})
