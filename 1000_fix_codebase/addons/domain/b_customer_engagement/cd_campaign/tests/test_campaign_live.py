"""Behavioural tests for M35 campaigns, attribution and the M10 hook (live ORM)."""

from datetime import date, datetime
from unittest.mock import patch

import pytest
from odoo import api
from odoo.exceptions import UserError


@pytest.fixture
def env(odoo_env):
    return odoo_env


def _campaign(env, **vals):
    vals.setdefault("name", "Eid Repair Fest/2026")
    return env["fix.campaign"].create(vals)


def _events(env, event_type, rec):
    return env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", rec.id)]
    )


def test_utm_code_and_cost_per_response(env):
    campaign = _campaign(env, channel="sms", budget=1000.0)
    assert campaign.utm_campaign == "eid_repair_fest_2026_sms"
    assert (campaign.response_count, campaign.cost_per_response) == (0, 0.0)
    responses = env["fix.campaign.response"]
    for kind in ("click", "call", "form"):
        responses.create({"campaign_id": campaign.id, "response_type": kind})
    assert campaign.response_count == 3
    assert campaign.cost_per_response == 333.33
    response = campaign.response_ids[0]
    assert (
        '"campaign": "Eid Repair Fest/2026"' in _events(env, "campaign.response", response).payload
    )


def test_launch_requires_a_draft_campaign_with_a_window(env):
    undated = _campaign(env)
    inverted = _campaign(env, start_date=date(2026, 11, 30), end_date=date(2026, 11, 1))
    ok = _campaign(env, start_date=date(2026, 11, 1), end_date=date(2026, 11, 30))
    with pytest.raises(UserError, match="runs between dates"), env.cr.savepoint():
        undated.action_launch()
    with pytest.raises(UserError, match="inverted"), env.cr.savepoint():
        inverted.action_launch()
    ok.action_launch()
    assert ok.state == "running"
    assert _events(env, "campaign.launched", ok)
    with pytest.raises(UserError, match="Launch from draft only"), env.cr.savepoint():
        ok.action_launch()


def _consent(env, partner, channel, state="granted", **vals):
    return env["fix.consent"].create(
        {"partner_id": partner.id, "channel": channel, "state": state, "proof": "OTP-1", **vals}
    )


def test_consent_is_never_assumed(env):
    assert _campaign(env).pdpa_consent_verified is False
    social = _campaign(env, start_date=date(2026, 11, 1), end_date=date(2026, 11, 30))
    social.action_launch()  # no individual is messaged on social
    assert (social.pdpa_consent_verified, social.recipient_count) == (False, 0)


def test_sms_launch_messages_only_consented_partners(env):
    tag = "CMPCONSENT"
    opted_in, all_channels, never, withdrawn, email_only = (
        env["res.partner"].create({"name": f"{tag} {n}"})
        for n in ("Opted", "Marketing", "Never", "Withdrawn", "EmailOnly")
    )
    _consent(env, opted_in, "sms")
    _consent(env, all_channels, "marketing")
    _consent(env, email_only, "email")
    grant = _consent(env, withdrawn, "sms", date_granted=datetime(2026, 1, 1))
    grant.action_withdraw()
    campaign = _campaign(
        env,
        channel="sms",
        audience_domain=f"[('name', '=like', '{tag} %')]",
        target_audience_type="custom_domain",
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 30),
    )
    campaign.action_launch()
    assert campaign.recipient_ids == opted_in | all_channels
    assert (campaign.recipient_count, campaign.excluded_no_consent_count) == (2, 3)
    assert campaign.pdpa_consent_verified is True
    payload = _events(env, "campaign.launched", campaign).payload
    assert '"recipients": 2' in payload and '"excluded_no_consent": 3' in payload
    assert never not in campaign.recipient_ids


def test_launch_fails_closed_without_consent_or_a_resolvable_segment(env):
    window = {"start_date": date(2026, 11, 1), "end_date": date(2026, 11, 30)}
    nobody = _campaign(
        env, channel="email", audience_domain="[('name', '=', 'CMP nobody at all')]", **window
    )
    with pytest.raises(UserError, match="granted email consent"), env.cr.savepoint():
        nobody.action_launch()
    assert (nobody.state, nobody.pdpa_consent_verified) == ("draft", False)
    dormant = _campaign(env, channel="sms", target_audience_type="dormant_90d", **window)
    with pytest.raises(UserError, match="explicit audience segment domain"), env.cr.savepoint():
        dormant.action_launch()
    broken = _campaign(env, channel="sms", audience_domain="[(", **window)
    with pytest.raises(UserError, match="not valid"), env.cr.savepoint():
        broken.action_launch()
    scalar = _campaign(env, channel="sms", audience_domain="42", **window)
    with pytest.raises(UserError, match="must be a list"), env.cr.savepoint():
        scalar.action_launch()


def test_pause_resume_complete_discipline(env):
    campaign = _campaign(env, start_date=date(2026, 11, 1), end_date=date(2026, 11, 30))
    with pytest.raises(UserError, match="Only a RUNNING campaign pauses"), env.cr.savepoint():
        campaign.action_pause()
    with pytest.raises(UserError, match="Only a PAUSED campaign resumes"), env.cr.savepoint():
        campaign.action_resume()
    with pytest.raises(UserError, match="Complete an active campaign"), env.cr.savepoint():
        campaign.action_complete()
    campaign.action_launch()
    campaign.action_pause()
    assert campaign.state == "paused"
    campaign.action_resume()
    assert campaign.state == "running"
    campaign.action_complete()
    assert campaign.state == "completed"
    assert _events(env, "campaign.completed", campaign)


@pytest.fixture
def loyalty(env):
    program = env["fix.loyalty.program"].create({"name": "CMP Privilege", "code": "CMPPRIV"})
    env["fix.loyalty.tier"].create({"program_id": program.id, "name": "Silver", "code": "SILVER"})
    return program


def _hook(env, campaign, program, **vals):
    return env["fix.loyalty.campaign.hook"].create(
        {"name": "Responder bonus", "campaign_id": campaign.id, "program_id": program.id, **vals}
    )


def test_loyalty_hook_posts_points_to_each_responder_once(env, loyalty):
    """Regression: the hook branch never ran (an empty recordset is falsy) and
    called a method the hook does not have - responders were marked rewarded
    while no point was ever posted."""
    campaign = _campaign(env)
    _hook(env, campaign, loyalty, bonus_points=150).action_activate()
    _hook(env, campaign, loyalty, bonus_points=999)  # still a draft: ignored
    ayesha = env["res.partner"].create({"name": "CMP Ayesha"})
    responses = env["fix.campaign.response"]
    rewarded = responses.create({"campaign_id": campaign.id, "partner_id": ayesha.id})
    anonymous = responses.create({"campaign_id": campaign.id})
    assert campaign.action_trigger_loyalty_hook() == 1
    assert campaign.action_trigger_loyalty_hook() == 0  # never twice
    account = env["fix.loyalty.account"].search([("partner_id", "=", ayesha.id)])
    assert account.points_balance == 150
    assert (rewarded.loyalty_points_awarded, rewarded.conversion_status) == (
        150,
        "enrolled_loyalty",
    )
    assert anonymous.conversion_status == "engaged"
    assert len(_events(env, "campaign.loyalty_rewards_disbursed", campaign)) == 2


def test_voucher_hooks_issue_vouchers(env, loyalty):
    campaign = _campaign(env)
    _hook(
        env, campaign, loyalty, reward_type="voucher", voucher_discount_value=300.0
    ).action_activate()
    karim = env["res.partner"].create({"name": "CMP Karim"})
    response = env["fix.campaign.response"].create(
        {"campaign_id": campaign.id, "partner_id": karim.id}
    )
    assert campaign.action_trigger_loyalty_hook() == 1
    voucher = env["fix.loyalty.voucher"].search([("partner_id", "=", karim.id)])
    assert (voucher.discount_value, voucher.state, voucher.campaign_id) == (
        300.0,
        "active",
        campaign,
    )
    assert (response.loyalty_points_awarded, response.conversion_status) == (0, "enrolled_loyalty")


def test_without_the_loyalty_module_nothing_is_awarded(env):
    campaign = _campaign(env)
    env["fix.campaign.response"].create(
        {"campaign_id": campaign.id, "partner_id": env["res.partner"].create({"name": "CMP X"}).id}
    )
    real_get = api.Environment.get

    def get_without_m10(self, key, default=None):
        return default if key == "fix.loyalty.campaign.hook" else real_get(self, key, default)

    with patch.object(api.Environment, "get", get_without_m10):
        assert campaign.action_trigger_loyalty_hook() == 0
    assert (
        '"rewards_awarded": 0'
        in _events(env, "campaign.loyalty_rewards_disbursed", campaign).payload
    )


def test_the_hook_runs_one_campaign_at_a_time(env):
    with pytest.raises(ValueError), env.cr.savepoint():
        (_campaign(env) | _campaign(env, name="Second")).action_trigger_loyalty_hook()
