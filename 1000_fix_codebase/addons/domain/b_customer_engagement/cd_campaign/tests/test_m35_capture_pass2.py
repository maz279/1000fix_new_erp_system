"""M35 capture audit, pass 2 (2026-11-19): what each sub-module page records
that the spec names and pass 1 did not give it. Driven as NON-ADMIN users
through the workspace endpoints wherever the workspace drives it (the
superuser is trusted by the model guards and would hide a gap).

  1 Planning & Approval: programme budget and period; capacity check blocks
    launch until the Operations Director overrides it (BRU-MKT-05); emergency
    stop cancels queued messages and exits every journey member (BRU-MKT-13).
  2 Audience: open complaints, credit hold and recent recipients are
    suppressed and shown in the estimate (FR-MKT-013, BRU-MKT-08); intersect.
  3 Journeys: conflict priority (BRU-MKT-06), exit on complaint and on
    conversion, manual exit with a reason (FR-MKT-019).
  4 Content: no approval without English and Bengali, Bengali script, known
    variables used alike, and an expiry (BRU-MKT-09/10); an expired creative
    blocks launch and the cron retires it.
  5 Experimentation: a winner only on significant figures (FR-MKT-031).
  6 Budget & Attribution: commitments count against the budget; 80% alert,
    100% pause (AUT-MKT-12); measured result against the holdout, never typed.
  7 Portal Advertising: one placement per slot at a time.
"""

import itertools
import types
from contextlib import contextmanager
from datetime import date, timedelta
from unittest import mock

import pytest
from odoo import Command, fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
OVERRIDE = "cd_campaign.group_capacity_override"
_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


def _ok(res):
    return bool(res) and not res.get("error") and bool(res.get("success") or res.get("id"))


@contextmanager
def _refused(env, match=None):
    with pytest.raises(REFUSED, match=match), env.cr.savepoint():
        yield


def _user(env, login, *xmlids):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": "%s.%d@m35p2.test" % (login, next(_SEQ)),
                "group_ids": [
                    Command.set([env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids])
                ],
            }
        )
    )


@pytest.fixture
def api():
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as generic

    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(generic, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(generic.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.clerk = _user(env, "m35p2_clerk")
    x.clerk_env = env(user=x.clerk.id)
    x.ops = _user(env, "m35p2_ops_director", OVERRIDE)
    x.ops_env = env(user=x.ops.id)
    Partner = env["res.partner"]
    x.p = [Partner.create({"name": "M35P2 Party %d" % i}) for i in range(1, 21)]
    n = next(_SEQ)
    Segment = env["fix.segment"]
    x.seg = Segment.create({"code": "M35P2-IN-%d" % n, "name": "M35P2 AC owners"})
    x.seg.action_add_members([p.id for p in x.p])
    x.seg_dhaka = Segment.create({"code": "M35P2-DH-%d" % n, "name": "M35P2 Dhaka"})
    x.seg_dhaka.action_add_members([p.id for p in x.p[:10]])
    x.campaign = env["fix.campaign"].create(
        {
            "name": "M35P2 Winter AC Service %d" % n,
            "channel": "social",
            "budget": 40000.0,
            "start_date": "2026-12-01",
            "end_date": "2026-12-31",
            "campaign_type": "seasonal",
            "target_audience_type": "segments",
            "segment_ids": [Command.set([x.seg.id])],
        }
    )
    return x


def _write(api, env, model, rid, values):
    return api(env, "model_write", model=model, record_id=rid, values=values)


def _act(api, env, model, ids, method, **kwargs):
    return api(env, "model_action", model=model, ids=ids, method=method, kwargs=kwargs)


# --- 1 Planning & Approval ------------------------------------------------------


def test_a_programme_caps_its_campaigns_budgets_and_period(w, api):
    res = _write(
        api,
        w.clerk_env,
        "fix.campaign.programme",
        False,
        {
            "code": "P2-WINTER-%d" % next(_SEQ),
            "name": "Winter 2026",
            "date_from": "2026-11-01",
            "date_to": "2027-01-31",
            "owner_id": w.clerk.id,
            "budget": 50000.0,
        },
    )
    assert _ok(res), res
    prog = w.env["fix.campaign.programme"].browse(res["id"])
    res = _write(api, w.clerk_env, "fix.campaign", w.campaign.id, {"programme_id": prog.id})
    assert _ok(res), res
    assert prog.campaign_count == 1 and prog.planned_budget == 40000.0
    with _refused(w.env, match="programme budget"):
        w.env["fix.campaign"].with_user(w.clerk).create(
            {
                "name": "M35P2 second",
                "channel": "social",
                "budget": 20000.0,
                "programme_id": prog.id,
                "start_date": "2026-12-01",
                "end_date": "2026-12-15",
            }
        )
    with _refused(w.env, match="ends after its programme"):
        w.campaign.with_user(w.clerk).write({"end_date": "2027-03-01"})


def test_capacity_check_blocks_launch_until_the_ops_director_overrides(w, api):
    vals = {
        "campaign_id": w.campaign.id,
        "expected_response_pct": 50.0,
        "available_capacity": 3,
        "capacity_source": "M02 roster, week 49",
    }
    res = _write(api, w.clerk_env, "fix.campaign.capacity.check", False, vals)
    assert not _ok(res), "a check before the estimate must be refused"
    w.campaign.with_user(w.clerk).action_estimate_audience()
    assert w.campaign.estimated_reach == 20
    res = _write(api, w.clerk_env, "fix.campaign.capacity.check", False, vals)
    assert _ok(res), res
    check = w.env["fix.campaign.capacity.check"].browse(res["id"])
    assert (check.reach_basis, check.projected_jobs, check.result) == (20, 10, "insufficient")
    assert w.campaign.capacity_check_result == "insufficient"
    # the check is evidence: not edited, its stamps not typed
    res = _write(
        api, w.clerk_env, "fix.campaign.capacity.check", check.id, {"available_capacity": 50}
    )
    assert not _ok(res) and check.available_capacity == 3
    with _refused(w.env):
        check.with_user(w.clerk).write({"state": "overridden"})
    with _refused(w.env, match="exceeds capacity"):
        w.campaign.with_user(w.clerk).action_launch()
    # only the Operations Director overrides, with a reason: a second clerk
    # (not the checker, so segregation of duties is not what stops them) cannot
    other_clerk = _user(w.env, "m35p2_clerk2")
    with _refused(w.env, match="Only the Operations Director"):
        check.with_user(other_clerk).action_override("crews added")
    res = _act(
        api, w.clerk_env, "fix.campaign.capacity.check", [check.id], "action_override", reason="x"
    )
    assert not _ok(res)
    res = _act(
        api, w.ops_env, "fix.campaign.capacity.check", [check.id], "action_override", reason=""
    )
    assert not _ok(res)
    res = _act(
        api,
        w.ops_env,
        "fix.campaign.capacity.check",
        [check.id],
        "action_override",
        reason="Two contract crews added for December",
    )
    assert _ok(res), res
    assert check.state == "overridden" and check.override_by_id == w.ops
    w.campaign.with_user(w.clerk).action_launch()
    assert w.campaign.state == "running"


def test_the_ops_director_cannot_override_their_own_check(w):
    w.campaign.with_user(w.ops).action_estimate_audience()
    check = (
        w.env["fix.campaign.capacity.check"]
        .with_user(w.ops)
        .create(
            {
                "campaign_id": w.campaign.id,
                "expected_response_pct": 80.0,
                "available_capacity": 1,
                "capacity_source": "branch plan",
            }
        )
    )
    with _refused(w.env, match="Segregation of duties"):
        check.with_user(w.ops).action_override("mine")


def test_emergency_stop_cancels_queued_messages_and_exits_every_member(w, api):
    w.campaign.with_user(w.clerk).action_launch()
    journey = (
        w.env["fix.campaign.journey"]
        .sudo()
        .create(
            {
                "name": "M35P2 reminder",
                "campaign_id": w.campaign.id,
                "journey_kind": "campaign_audience",
            }
        )
    )
    journey.sudo().write({"state": "active"})
    members = journey._enrol(w.env["res.partner"].browse([p.id for p in w.p[:3]]))
    assert members == 3
    member = journey.member_ids[:1]
    queued = (
        w.env["fix.notif.delivery"]
        .sudo()
        .create(
            {
                "partner_id": w.p[0].id,
                "channel": "sms",
                "to_address": "+8801700000000",
                "purpose": "marketing",
                "body": "Winter AC check",
                "source_model": "fix.campaign.journey.member",
                "source_id": member.id,
            }
        )
    )
    queued.sudo().write({"state": "queued"})
    res = _act(
        api, w.clerk_env, "fix.campaign", [w.campaign.id], "action_emergency_stop", reason=""
    )
    assert not _ok(res) and w.campaign.state == "running"
    res = _act(
        api,
        w.clerk_env,
        "fix.campaign",
        [w.campaign.id],
        "action_emergency_stop",
        reason="Wrong price in the banner",
    )
    assert _ok(res), res
    assert w.campaign.state == "halted" and w.campaign.halted_by_id == w.clerk
    assert queued.state == "cancelled" and w.campaign.halt_cancelled_count == 1
    assert set(journey.member_ids.mapped("state")) == {"exited"}
    assert journey.state == "paused"
    with _refused(w.env, match="does not resume"):
        w.campaign.with_user(w.clerk).action_resume()
    with _refused(w.env):
        w.campaign.with_user(w.clerk).write({"halt_reason": "forged"})


def test_the_calendar_flags_a_clash_on_the_same_channel_and_segment(w):
    other = w.env["fix.campaign"].create(
        {
            "name": "M35P2 overlap",
            "channel": "social",
            "budget": 1000.0,
            "start_date": "2026-12-20",
            "end_date": "2027-01-10",
            "target_audience_type": "segments",
            "segment_ids": [Command.set([w.seg.id])],
        }
    )
    assert other.name in (w.campaign.calendar_conflicts or "")
    other.write({"channel": "email"})
    w.campaign.invalidate_recordset(["calendar_conflicts"])
    assert other.name not in (w.campaign.calendar_conflicts or "")


def test_the_landing_page_is_https_and_tracked(w, api):
    res = _write(
        api, w.clerk_env, "fix.campaign", w.campaign.id, {"landing_page_url": "http://x.y"}
    )
    assert not _ok(res)
    res = _write(
        api,
        w.clerk_env,
        "fix.campaign",
        w.campaign.id,
        {"landing_page_url": "https://1000fix.com/ac"},
    )
    assert _ok(res), res
    assert w.campaign.tracked_url.startswith("https://1000fix.com/ac?utm_source=")


# --- 2 Audience -------------------------------------------------------------


def _complaint(env, partner):
    ou = env["operating.unit"].search([], limit=1)
    return env["fix.complaint"].create(
        {
            "operating_unit_id": ou.id,
            "name": "M35P2 complaint",
            "customer_id": partner.id,
            "description": "Late repair",
            "severity": "minor",
        }
    )


def test_suppression_and_intersect_shape_the_estimate(w, api):
    if "fix.complaint" not in w.env:
        pytest.skip("M34 complaints not installed")
    _complaint(w.env, w.p[0])
    res = _write(
        api,
        w.clerk_env,
        "fix.campaign",
        w.campaign.id,
        {"intersect_segment_ids": [w.seg_dhaka.id], "suppress_open_complaints": True},
    )
    assert _ok(res), res
    res = _act(api, w.clerk_env, "fix.campaign", [w.campaign.id], "action_estimate_audience")
    assert _ok(res), res
    # 10 in Dhaka, one with an open complaint
    assert w.campaign.estimated_reach == 9
    assert "1 open complaints" in w.campaign.estimate_breakdown
    w.campaign.write({"suppress_open_complaints": False})
    w.campaign.action_estimate_audience()
    assert w.campaign.estimated_reach == 10


def test_recent_recipients_and_credit_hold_are_suppressed(w):
    earlier = w.env["fix.campaign"].create(
        {"name": "M35P2 earlier", "channel": "social", "budget": 10.0, "start_date": date.today()}
    )
    earlier.sudo().write({"state": "completed", "recipient_ids": [Command.set([w.p[1].id])]})
    w.campaign.write({"suppress_recent_days": 30, "suppress_open_complaints": False})
    assert w.p[1].id in w.campaign._suppressed()["recent"]
    if "fix.credit.profile" in w.env:
        w.env["fix.credit.profile"].sudo().create({"customer_id": w.p[2].id, "credit_hold": True})
        w.campaign.write({"suppress_credit_hold": True})
        assert w.p[2].id in w.campaign._suppressed()["credit_hold"]
    w.campaign.action_estimate_audience()
    assert w.p[1].id not in w.env["res.partner"].search(w.campaign._audience_domain()).ids


def test_suppression_is_fixed_once_launched(w):
    w.campaign.action_launch()
    with _refused(w.env, match="fixed once it has launched"):
        w.campaign.with_user(w.clerk).write({"suppress_open_complaints": False})


# --- 3 Journeys ------------------------------------------------------------


def _journey(w, name, priority, group="winter"):
    j = (
        w.env["fix.campaign.journey"]
        .sudo()
        .create(
            {
                "name": name,
                "campaign_id": w.campaign.id,
                "journey_kind": "campaign_audience",
                "priority": priority,
                "conflict_group": group,
            }
        )
    )
    j.sudo().write({"state": "active"})
    return j


def test_the_higher_priority_journey_wins_a_conflict(w):
    w.campaign.action_launch()
    low = _journey(w, "M35P2 nurture", 5)
    high = _journey(w, "M35P2 renewal", 1)
    party = w.env["res.partner"].browse(w.p[0].id)
    assert low._enrol(party) == 1
    assert high._enrol(party) == 1
    low_member = low.member_ids.filtered(lambda m: m.partner_id == party)
    assert low_member.state == "exited" and "higher-priority" in low_member.exit_reason
    # entering the lower one again while in the higher one: not entered
    other = w.env["res.partner"].browse(w.p[1].id)
    high._enrol(other)
    assert low._enrol(other) == 0


def test_a_complaint_or_a_conversion_exits_the_member(w):
    w.campaign.action_launch()
    j = _journey(w, "M35P2 exits", 3, group=False)
    j._enrol(w.env["res.partner"].browse([w.p[0].id, w.p[1].id]))
    m0, m1 = (j.member_ids.filtered(lambda m, p=p: m.partner_id == p) for p in (w.p[0], w.p[1]))
    assert j._runtime_member_still_eligible(m0)[0]
    if "fix.complaint" in w.env:
        _complaint(w.env, w.p[0])
        ok, why = j._runtime_member_still_eligible(m0)
        assert not ok and "complaint" in why
    w.env["fix.campaign.touch"].sudo().create(
        {
            "campaign_id": w.campaign.id,
            "partner_id": w.p[1].id,
            "touch_type": "conversion",
            "occurred_at": fields.Datetime.now() + timedelta(seconds=5),
        }
    )
    ok, why = j._runtime_member_still_eligible(m1)
    assert not ok and "converted" in why


def test_a_member_is_exited_by_hand_with_a_reason(w, api):
    w.campaign.action_launch()
    j = _journey(w, "M35P2 manual", 3, group=False)
    j._enrol(w.env["res.partner"].browse(w.p[0].id))
    member = j.member_ids
    res = _act(
        api, w.clerk_env, "fix.campaign.journey.member", member.ids, "action_exit_member", reason=""
    )
    assert not _ok(res)
    res = _act(
        api,
        w.clerk_env,
        "fix.campaign.journey.member",
        member.ids,
        "action_exit_member",
        reason="Complained by phone",
    )
    assert _ok(res), res
    assert member.state == "exited" and "Complained by phone" in member.exit_reason


def test_the_holdout_never_enters_a_journey(w):
    w.campaign.sudo().write({"holdout_partner_ids": [Command.set([w.p[0].id])]})
    w.campaign.action_launch()
    j = _journey(w, "M35P2 holdout", 3, group=False)
    assert j._enrol(w.env["res.partner"].browse([w.p[0].id, w.p[1].id])) == 1


# --- 4 Content -------------------------------------------------------------


def _creative(w, **vals):
    return (
        w.env["fix.campaign.creative"]
        .with_user(w.clerk)
        .create(
            {
                "name": "M35P2 SMS copy",
                "campaign_id": w.campaign.id,
                "asset_type": "copy",
                "reference": "s3://m35/p2-copy",
                **vals,
            }
        )
    )


def test_content_needs_both_languages_known_variables_and_an_expiry(w, api):
    c = _creative(w, body_en="Hi {name}, book your AC service")
    with _refused(w.env, match="needs its copy in both English and Bengali"):
        c.action_request_approval()
    c.write({"body_bn": "Hi {name}, AC service"})
    with _refused(w.env, match="no Bengali script"):
        c.action_request_approval()
    c.write({"body_bn": "{name}, আপনার এসি সার্ভিস বুক করুন"})
    with _refused(w.env, match="expiry date"):
        c.action_request_approval()
    c.write({"expires_on": "2099-12-31", "body_en": "Hi {name}, use {code}"})
    with _refused(w.env, match="cannot fill"):
        c.action_request_approval()
    c.write({"body_en": "Hi {name} with your {device}"})
    with _refused(w.env, match="personalise differently"):
        c.action_request_approval()
    c.write({"body_en": "Hi {name}, book your AC service"})
    assert c.placeholders == "{name}"
    assert c.sms_segments_en == 1 and c.sms_segments_bn == 1
    res = _act(
        api,
        w.clerk_env,
        "fix.campaign.creative",
        c.ids,
        "action_request_approval",
        justification="ok",
    )
    assert _ok(res), res
    # pending content is frozen, its copy included
    with _refused(w.env, match="Withdraw it"):
        c.with_user(w.clerk).write({"body_bn": "{name}, নতুন"})


def test_a_visual_asset_needs_its_bengali_version(w):
    c = _creative(w, asset_type="image", expires_on="2099-12-31")
    with _refused(w.env, match="Bengali version"):
        c.action_request_approval()


def test_an_expired_creative_blocks_launch_and_is_retired(w):
    c = _creative(w, body_en="x", body_bn="এসি", expires_on=date.today() - timedelta(days=1))
    c.sudo().write({"state": "approved"})
    with _refused(w.env, match="expired"):
        w.campaign.action_launch()
    soon = _creative(
        w,
        name="M35P2 soon",
        body_en="y",
        body_bn="এসি",
        expires_on=date.today() + timedelta(days=3),
    )
    soon.sudo().write({"state": "approved"})
    out = w.env["fix.campaign"].cron_retire_expired_creatives()
    assert c.state == "retired" and soon.expiry_notified
    assert out["retired"] >= 1


def test_the_version_is_never_typed(w):
    c = _creative(w)
    with _refused(w.env):
        c.with_user(w.clerk).write({"version": 7})


# --- 5 Experimentation -------------------------------------------------------


def test_a_winner_is_named_only_on_significant_figures(w, api):
    exp = (
        w.env["fix.campaign.experiment"]
        .with_user(w.clerk)
        .create(
            {"name": "M35P2 Bangla vs English", "campaign_id": w.campaign.id, "variable": "content"}
        )
    )
    exp.action_start()
    base = {"note": "n=1000 each"}
    figures = {"a_sample": 1000, "a_conversions": 52, "b_sample": 1000, "b_conversions": 48}
    with _refused(w.env, match="not significant"):
        exp.with_user(w.clerk).action_conclude(winner="a", **base, **figures)
    with _refused(w.env, match="Enter how many"):
        exp.with_user(w.clerk).action_conclude(winner="none", **base)
    with _refused(w.env, match="converted no more"):
        exp.with_user(w.clerk).action_conclude(
            winner="none", **base, a_sample=10, a_conversions=11, b_sample=10, b_conversions=1
        )
    strong = {"a_sample": 6000, "a_conversions": 246, "b_sample": 6000, "b_conversions": 174}
    with _refused(w.env, match="significant"):
        exp.with_user(w.clerk).action_conclude(winner="none", **base, **strong)
    with _refused(w.env, match="converted less"):
        exp.with_user(w.clerk).action_conclude(winner="b", **base, **strong)
    res = _act(
        api,
        w.clerk_env,
        "fix.campaign.experiment",
        exp.ids,
        "action_conclude",
        winner="a",
        **base,
        **strong,
    )
    assert _ok(res), res
    assert exp.state == "concluded" and exp.winner == "a"
    assert exp.p_value < 0.05 and exp.significance > 95.0
    assert round(exp.a_rate, 2) == 4.1
    with _refused(w.env):
        exp.with_user(w.clerk).write({"a_conversions": 999})


# --- 6 Budget & Attribution --------------------------------------------------


def test_a_commitment_counts_against_the_budget_until_invoiced(w, api):
    res = _write(
        api,
        w.clerk_env,
        "fix.campaign.spend",
        False,
        {
            "campaign_id": w.campaign.id,
            "name": "Billboard, Gulshan",
            "category": "print",
            "stage": "committed",
            "amount": 30000.0,
        },
    )
    assert _ok(res), res
    spend = w.env["fix.campaign.spend"].browse(res["id"])
    w.campaign.invalidate_recordset()
    assert w.campaign.committed_spend == 30000.0 and w.campaign.actual_spend == 0.0
    assert w.campaign.budget_available == 10000.0
    assert not w.campaign.budget_alert_80_at  # 75%: below the alert
    with _refused(w.env, match="spent and committed"):
        w.env["fix.campaign.spend"].with_user(w.clerk).create(
            {"campaign_id": w.campaign.id, "name": "Radio", "amount": 15000.0}
        )
    with _refused(w.env, match="Mark Invoiced"):
        spend.with_user(w.clerk).write({"stage": "incurred"})
    res = _act(
        api,
        w.clerk_env,
        "fix.campaign.spend",
        spend.ids,
        "action_mark_incurred",
        reference="INV-77",
    )
    assert _ok(res), res
    w.campaign.invalidate_recordset()
    assert spend.stage == "incurred" and spend.reference == "INV-77" and spend.incurred_on
    assert w.campaign.committed_spend == 0.0 and w.campaign.actual_spend == 30000.0


def test_budget_alerts_at_80_and_a_pause_at_100(w):
    w.campaign.action_launch()
    Spend = w.env["fix.campaign.spend"].with_user(w.clerk)
    Spend.create({"campaign_id": w.campaign.id, "name": "Media 1", "amount": 30000.0})
    assert not w.campaign.budget_alert_80_at
    Spend.create({"campaign_id": w.campaign.id, "name": "Media 2", "amount": 4000.0})
    assert w.campaign.budget_alert_80_at and w.campaign.state == "running"
    Spend.create({"campaign_id": w.campaign.id, "name": "Media 3", "amount": 6000.0})
    assert w.campaign.state == "paused"


def test_a_campaign_is_measured_against_its_holdout(w, api):
    treated = w.env["res.partner"].browse([p.id for p in w.p[:10]])
    held = w.env["res.partner"].browse([p.id for p in w.p[10:15]])
    res = _act(api, w.clerk_env, "fix.campaign", [w.campaign.id], "action_measure")
    assert not _ok(res), "a draft campaign is not measured"
    w.campaign.sudo().write(
        {
            "state": "completed",
            "recipient_ids": [Command.set(treated.ids)],
            "holdout_partner_ids": [Command.set(held.ids)],
        }
    )
    revenue = {treated[0].id: 5000.0, treated[1].id: 3000.0, held[0].id: 1000.0}
    Result = type(w.env["fix.attribution.result"])
    with mock.patch.object(
        Result,
        "_revenue_by_party",
        lambda self, ids, a, b: {k: v for k, v in revenue.items() if k in ids},
    ):
        res = _act(api, w.clerk_env, "fix.campaign", [w.campaign.id], "action_measure")
    assert _ok(res), res
    r = w.campaign.result_ids
    assert len(r) == 1
    assert (r.treated_count, r.holdout_count, r.treated_converters, r.holdout_converters) == (
        10,
        5,
        2,
        1,
    )
    assert (r.treated_rate, r.holdout_rate) == (20.0, 20.0)
    # holdout spent 1000 over 5 heads: baseline 200 x 10 = 2000; 8000 - 2000
    assert (r.holdout_baseline, r.incremental_revenue) == (2000.0, 6000.0)
    # the result is never typed, edited or deleted
    res = _write(api, w.clerk_env, "fix.attribution.result", r.id, {"incremental_revenue": 1.0})
    assert not _ok(res)
    with _refused(w.env):
        w.env["fix.attribution.result"].with_user(w.clerk).create({"campaign_id": w.campaign.id})
    # the model refuses a typed result even where access rights would allow it
    with _refused(w.env, match="measured from the campaign"):
        w.env["fix.attribution.result"].sudo().create({"campaign_id": w.campaign.id})
    with _refused(w.env, match="measure again"):
        r.sudo().write({"incremental_revenue": 1.0})
    with _refused(w.env):
        r.sudo().unlink()


def test_revenue_is_what_was_invoiced_in_the_window(w):
    if "account.move" not in w.env:
        pytest.skip("invoicing not installed")
    Result = w.env["fix.attribution.result"]
    party = w.p[3]
    move = (
        w.env["account.move"]
        .sudo()
        .create(
            {
                "move_type": "out_invoice",
                "partner_id": party.id,
                "invoice_date": "2026-12-05",
                "invoice_line_ids": [
                    Command.create(
                        {"name": "AC service", "quantity": 1, "price_unit": 2500.0, "tax_ids": []}
                    )
                ],
            }
        )
    )
    try:
        with w.env.cr.savepoint():
            move.action_post()
    except Exception as exc:  # an estate posting gate (DOFA, period lock) is not this test
        pytest.skip("posting refused on this database: %s" % exc)
    got = Result._revenue_by_party({party.id}, date(2026, 12, 1), date(2026, 12, 31))
    assert got == {party.id: 2500.0}
    assert Result._revenue_by_party({party.id}, date(2027, 1, 1), date(2027, 1, 31)) == {}


# --- 7 Portal Advertising -----------------------------------------------------


def test_one_placement_per_slot_at_a_time(w, api):
    Ad = w.env["fix.campaign.ad"].with_user(w.clerk)
    ctx = "m35p2-%d" % next(_SEQ)
    Ad.create(
        {
            "name": "Walton banner",
            "campaign_id": w.campaign.id,
            "placement": "checkout",
            "page_context": ctx,
            "position": 1,
            "active_from": "2026-12-01",
            "active_to": "2026-12-31",
        }
    )
    with _refused(w.env, match="already holds that slot"):
        Ad.create(
            {
                "name": "Samsung banner",
                "campaign_id": w.campaign.id,
                "placement": "checkout",
                "page_context": ctx,
                "position": 1,
                "active_from": "2026-12-20",
                "active_to": "2027-01-10",
            }
        )
    res = _write(
        api,
        w.clerk_env,
        "fix.campaign.ad",
        False,
        {
            "name": "Samsung banner",
            "campaign_id": w.campaign.id,
            "placement": "checkout",
            "page_context": ctx,
            "position": 2,
            "active_from": "2026-12-20",
            "active_to": "2027-01-10",
        },
    )
    assert _ok(res), res
