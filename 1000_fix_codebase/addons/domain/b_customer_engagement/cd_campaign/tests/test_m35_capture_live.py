"""M35 capture audit (2026-11-14): what the sub-module pages now capture,
driven as NON-ADMIN users through the workspace endpoints (the superuser is
trusted by the model guards and would hide a gap).

  * Audience from Segments: a draft campaign's audience is composed from
    governed M33 segments (include minus exclude), with a deterministic
    holdout; Estimate Reach writes the post-suppression figure; the audience
    is fixed once the campaign launches; the estimate is never typed.
  * Budget & Attribution: spend booked outside the estate counts as recorded
    spend; spend past the approved budget is refused (BRU-MKT-11); a
    recorded spend is voided with a reason, never edited or deleted. The
    attribution model is versioned, configured by the Marketing Manager only,
    frozen once in force, and pinned on a campaign when it completes
    (BRU-MKT-12).
  * Experimentation: the state and the winner move only through Start and
    Conclude; a started experiment's design is fixed.
  * Co-Marketing: a Channel Officer names the partners; a plain clerk cannot;
    the report shows the partner fund.
  * The touch ledger is not written by hand.
"""

import itertools
import types
from contextlib import contextmanager
from unittest import mock

import pytest
from odoo import Command
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
OFFICER = "cd_partner.group_fix_channel_officer"
MANAGER = "cd_campaign.group_marketing_manager"
_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


def _ok(res):
    """The write endpoint answers {id, display_name}; the action one {success}."""
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
                "login": "%s.%d@m35.test" % (login, next(_SEQ)),
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
    x.clerk = _user(env, "m35_clerk")
    x.manager = _user(env, "m35_manager", MANAGER)
    x.clerk_env = env(user=x.clerk.id)
    Partner = env["res.partner"]
    x.p = [Partner.create({"name": "M35 Party %d" % i}) for i in range(1, 41)]
    Segment = env["fix.segment"]
    n = next(_SEQ)
    x.seg_in = Segment.create({"code": "M35-IN-%d" % n, "name": "M35 AC owners"})
    x.seg_out = Segment.create({"code": "M35-OUT-%d" % n, "name": "M35 open complaints"})
    x.seg_in.action_add_members([p.id for p in x.p])
    x.seg_out.action_add_members([x.p[0].id, x.p[1].id])
    x.campaign = env["fix.campaign"].create(
        {
            "name": "M35 Summer AC Service",
            "channel": "social",
            "budget": 40000.0,
            "start_date": "2026-11-15",
            "end_date": "2026-12-15",
        }
    )
    return x


# --- 2 Audience from Segments -------------------------------------------------


def test_a_clerk_defines_a_segment_audience_and_estimates_its_reach(w, api):
    res = api(
        w.clerk_env,
        "model_write",
        model="fix.campaign",
        record_id=w.campaign.id,
        values={
            "target_audience_type": "segments",
            "segment_ids": [w.seg_in.id],
            "exclude_segment_ids": [w.seg_out.id],
            "holdout_pct": 10,
        },
    )
    assert _ok(res), res
    res = api(
        w.clerk_env,
        "model_action",
        model="fix.campaign",
        ids=[w.campaign.id],
        method="action_estimate_audience",
        kwargs={},
    )
    assert _ok(res), res
    w.campaign.invalidate_recordset()
    audience = w.env["res.partner"].search(w.campaign._audience_domain())
    assert set(audience.ids) == {p.id for p in w.p[2:]}  # 38: include minus exclude
    held = w.campaign._holdout_of(audience)
    assert w.campaign.estimated_reach == 38 - len(held)
    assert w.campaign.estimated_at
    assert "38 in the audience" in w.campaign.estimate_breakdown


def test_a_segment_audience_names_a_segment(w):
    with _refused(w.env, match="at least one M33 segment"):
        w.campaign.with_user(w.clerk).write({"target_audience_type": "segments"})


def test_the_holdout_is_capped_and_deterministic(w):
    with _refused(w.env, match="between 0 and 50"):
        w.campaign.with_user(w.clerk).write({"holdout_pct": 60})
    twin = w.campaign.copy({"name": "M35 Winter Geyser"})
    partners = w.env["res.partner"].browse([p.id for p in w.p])
    for rec in (w.campaign, twin):
        rec.write({"holdout_pct": 30, "holdout_key": "EXP-AC-2026"})
    first = w.campaign._holdout_of(partners)
    assert first == w.campaign._holdout_of(partners)  # same every time
    assert first == twin._holdout_of(partners)  # shared key: one holdout group
    assert 0 < len(first) < len(partners)


def test_changing_the_audience_clears_a_stale_estimate(w):
    w.campaign.write({"target_audience_type": "segments", "segment_ids": [(6, 0, [w.seg_in.id])]})
    w.campaign.with_user(w.clerk).action_estimate_audience()
    assert w.campaign.estimated_at
    w.campaign.with_user(w.clerk).write({"exclude_segment_ids": [(6, 0, [w.seg_out.id])]})
    assert not w.campaign.estimated_at and not w.campaign.estimated_reach


def test_the_estimate_is_never_typed(w, api):
    res = api(
        w.clerk_env,
        "model_write",
        model="fix.campaign",
        record_id=w.campaign.id,
        values={"estimated_reach": 250000},
    )
    assert not _ok(res)
    with _refused(w.env):
        w.campaign.with_user(w.clerk).write({"estimated_reach": 250000})


def test_the_audience_is_fixed_once_launched(w):
    w.campaign.write({"target_audience_type": "segments", "segment_ids": [(6, 0, [w.seg_in.id])]})
    w.campaign.with_user(w.clerk).action_launch()
    assert w.campaign.state == "running"
    with _refused(w.env, match="fixed once it has launched"):
        w.campaign.with_user(w.clerk).write({"segment_ids": [(6, 0, [w.seg_out.id])]})


def test_an_addressed_launch_keeps_the_holdout_out_of_the_recipients(w):
    """BRU-MKT-14: the holdout receives nothing and is recorded."""
    camp = w.campaign
    partners = w.env["res.partner"].browse([p.id for p in w.p])
    camp.write({"holdout_pct": 25})
    with (
        mock.patch.object(
            type(camp), "_audience_domain", lambda self: [("id", "in", partners.ids)]
        ),
        mock.patch.object(type(camp), "_consented", lambda self, domain: partners),
        mock.patch.object(type(camp), "_dnd_reachable", lambda self, p: p),
        mock.patch.object(type(camp), "_btrc_within_curfew", lambda self: True),
        mock.patch.object(type(camp), "_assert_btrc_launch_allowed", lambda self: None),
    ):
        camp.write({"channel": "sms"})
        camp.with_user(w.clerk).action_launch()
    held = camp.holdout_partner_ids
    assert held and camp.recipient_ids
    assert not held & camp.recipient_ids
    assert len(held) + len(camp.recipient_ids) == len(partners)


# --- 6 Budget & Attribution ---------------------------------------------------


def _spend(w, amount, **kw):
    vals = {"campaign_id": w.campaign.id, "name": "Facebook boost", "amount": amount, **kw}
    return w.env["fix.campaign.spend"].with_user(w.clerk).create(vals)


def test_recorded_spend_counts_against_the_budget(w, api):
    before = w.campaign.actual_spend
    res = api(
        w.clerk_env,
        "model_write",
        model="fix.campaign.spend",
        record_id=False,
        values={
            "campaign_id": w.campaign.id,
            "name": "Prothom Alo half page",
            "category": "print",
            "amount": 15000.0,
            "reference": "INV-4471",
        },
    )
    assert _ok(res), res
    w.campaign.invalidate_recordset()
    assert w.campaign.actual_spend == pytest.approx(before + 15000.0)


def test_spend_past_the_approved_budget_is_refused(w):
    _spend(w, 30000.0)
    with _refused(w.env, match="BRU-MKT-11"):
        _spend(w, 10001.0)
    _spend(w, 10000.0)  # exactly the budget is allowed


def test_a_recorded_spend_is_voided_never_edited_or_deleted(w, api):
    spend = _spend(w, 5000.0)
    with _refused(w.env, match="not edited"):
        spend.with_user(w.clerk).write({"amount": 50.0})
    with _refused(w.env, match="never deleted"):
        spend.with_user(w.clerk).unlink()
    res = api(
        w.clerk_env,
        "model_action",
        model="fix.campaign.spend",
        ids=[spend.id],
        method="action_void",
        kwargs={},
    )
    assert not _ok(res)  # no reason, no void
    res = api(
        w.clerk_env,
        "model_action",
        model="fix.campaign.spend",
        ids=[spend.id],
        method="action_void",
        kwargs={"reason": "Duplicate of INV-4471"},
    )
    assert _ok(res), res
    assert spend.state == "void" and spend.voided_by_id == w.clerk
    w.campaign.invalidate_recordset()
    assert w.campaign.actual_spend == pytest.approx(0.0)


def test_only_the_marketing_manager_configures_attribution(w, api):
    res = api(
        w.clerk_env,
        "model_write",
        model="fix.attribution.model",
        record_id=False,
        values={"code": "MTA", "name": "Position", "method": "position", "lookback_days": 90},
    )
    assert not _ok(res)
    with _refused(w.env):
        w.env["fix.attribution.model"].with_user(w.clerk).create(
            {"code": "MTA", "name": "Position", "method": "position"}
        )


def test_the_attribution_model_is_versioned_and_frozen_in_force(w):
    Model = w.env["fix.attribution.model"].with_user(w.manager)
    code = "MTA-%d" % next(_SEQ)
    v1 = Model.create({"code": code, "name": "Position 40/20/40", "method": "position"})
    v1.action_activate()
    assert (v1.version, v1.state) == (1, "active")
    with _refused(w.env, match="BRU-MKT-12"):
        v1.write({"lookback_days": 30})
    with _refused(w.env, match="kept"):
        v1.unlink()
    v2 = Model.create({"code": code, "name": "Time decay", "method": "time_decay"})
    assert v2.version == 2
    v2.action_activate()
    assert v1.state == "superseded" and v2.state == "active"
    with _refused(w.env, match="Put In Force"):
        Model.create({"code": code, "name": "Forged", "method": "linear"}).write(
            {"state": "active"}
        )


def test_a_completed_campaign_keeps_the_model_then_in_force(w, api):
    Model = w.env["fix.attribution.model"].with_user(w.manager)
    code = "MTA-%d" % next(_SEQ)
    v1 = Model.create({"code": code, "name": "Linear", "method": "linear"})
    v1.action_activate()
    w.campaign.with_user(w.clerk).action_launch()
    w.campaign.with_user(w.clerk).action_complete()
    assert w.campaign.attribution_model_id == v1
    v2 = Model.create({"code": code, "name": "Last touch", "method": "last_touch"})
    v2.action_activate()
    assert w.campaign.attribution_model_id == v1  # not restated
    res = api(w.clerk_env, "model_report", module="M35", report="attribution_roi", params={})
    row = next(r for r in res["rows"] if r["campaign"] == w.campaign.name)
    assert row["model"] == v1.display_label


# --- 5 Experimentation --------------------------------------------------------


def test_an_experiment_moves_only_through_start_and_conclude(w, api):
    exp = (
        w.env["fix.campaign.experiment"]
        .with_user(w.clerk)
        .create(
            {"name": "Bangla vs English SMS", "campaign_id": w.campaign.id, "variable": "content"}
        )
    )
    res = api(
        w.clerk_env,
        "model_write",
        model="fix.campaign.experiment",
        record_id=exp.id,
        values={"state": "concluded"},
    )
    assert not _ok(res) or exp.state == "draft"
    with _refused(w.env):
        exp.with_user(w.clerk).write({"state": "concluded", "winner": "a"})
    exp.with_user(w.clerk).action_start()
    assert exp.state == "running"
    with _refused(w.env, match="design of a started experiment"):
        exp.with_user(w.clerk).write({"variant_a_pct": 80})
    with _refused(w.env, match="Name the winner"):
        exp.with_user(w.clerk).action_conclude(winner="", note="x")
    with _refused(w.env, match="Record the finding"):
        exp.with_user(w.clerk).action_conclude(winner="a", note="")
    res = api(
        w.clerk_env,
        "model_action",
        model="fix.campaign.experiment",
        ids=[exp.id],
        method="action_conclude",
        kwargs={
            "winner": "a",
            "note": "A 4.1% vs B 2.9% response, n=12,000",
            # capture pass 2: the winner is judged on the figures (FR-MKT-031)
            "a_sample": 6000,
            "a_conversions": 246,
            "b_sample": 6000,
            "b_conversions": 174,
        },
    )
    assert _ok(res), res
    assert (exp.state, exp.winner, exp.concluded_by_id) == ("concluded", "a", w.clerk)


# --- 7 Portal Advertising -----------------------------------------------------


def test_an_ad_placement_runs_forward(w):
    with _refused(w.env, match="ends after it starts"):
        w.env["fix.campaign.ad"].with_user(w.clerk).create(
            {
                "name": "Walton fridge banner",
                "campaign_id": w.campaign.id,
                "active_from": "2026-12-01",
                "active_to": "2026-11-01",
            }
        )


# --- 8 Co-Marketing -----------------------------------------------------------


def test_a_channel_officer_names_the_co_marketing_partners(w, api):
    if "partner_ids" not in w.env["fix.campaign"]._fields:
        pytest.skip("cd_partner not installed")
    officer = _user(w.env, "m35_officer", OFFICER)
    contact = w.env["res.partner"].create({"name": "M35 Brand Partner"})
    partner = w.env["fix.partner"].create(
        {
            "name": "M35 Brand Partner",
            "partner_id": contact.id,
            "partner_type": "alliance",
            "tin_number": "123456789012",
            "trade_license_no": "TL-M35",
        }
    )
    partner.write({"state": "onboarded"})
    res = api(
        w.clerk_env,
        "model_write",
        model="fix.campaign",
        record_id=w.campaign.id,
        values={"partner_ids": [partner.id]},
    )
    assert not _ok(res)
    res = api(
        w.env(user=officer.id),
        "model_write",
        model="fix.campaign",
        record_id=w.campaign.id,
        values={"partner_ids": [partner.id]},
    )
    assert _ok(res), res
    report = api(
        w.clerk_env, "model_report", module="M35", report="co_marketing_partner", params={}
    )
    row = next(r for r in report["rows"] if r["campaign"] == w.campaign.name)
    assert row["partners"] == "M35 Brand Partner"


# --- the touch ledger ---------------------------------------------------------


def test_the_touch_ledger_is_not_written_by_hand(w):
    with _refused(w.env):
        w.env["fix.campaign.touch"].with_user(w.clerk).create(
            {
                "campaign_id": w.campaign.id,
                "partner_id": w.p[0].id,
                "touch_type": "conversion",
                "value_bdt": 999999.0,
                "value_known": True,
            }
        )
