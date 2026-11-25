"""A03 P2 — M35 campaign lifecycle repairs (findings G-M35-4 … G-M35-10).

Every control is exercised by NON-ADMIN users holding only the groups named,
because the superuser is trusted by the field guards and would hide the gaps
the audit found. Fixture data (parties, consents, the DND registry, templates)
is set up as superuser; the actions under test run as the marketer or the
approver. Each control is checked both ways: the bad case is refused and the
legitimate path works.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from freezegun import freeze_time
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, inbox_task
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

# 10:00 BST, inside the BTRC 08:00-22:00 window.
IN_WINDOW = "2026-11-03 04:00:00"
T2 = "cd_entity_config.group_dofa_tier_2"
M35_JS = (
    Path(__file__).resolve().parents[4]
    / "platform"
    / "cd_p03_portal"
    / "static"
    / "src"
    / "a03"
    / "m35.js"
)


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def make_user(env):
    """A user holding exactly base.group_user plus the named groups."""
    seq = iter(range(1, 1000))

    def _make(*xmlids):
        n = next(seq)
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return env["res.users"].create(
            {
                "name": "M35 P2 user %d" % n,
                "login": "m35.p2.user.%d@example.com" % n,
                "group_ids": [(6, 0, groups)],
            }
        )

    return _make


@pytest.fixture
def marketer(make_user):
    return make_user()


def _notice(env):
    Notice = env["fix.transparency.notice"]
    notice = Notice.search([("version", "=", "v-m35-p2")], limit=1)
    return notice or Notice.create(
        {"version": "v-m35-p2", "text_bn": "পরীক্ষামূলক নোটিশ", "text_en": "M35 P2 notice"}
    )


def _party(env, tag, name, phone, channel="sms"):
    partner = env["res.partner"].create({"name": "%s %s" % (tag, name), "phone": phone})
    if channel:
        env["fix.consent"].create(
            {
                "partner_id": partner.id,
                "channel": channel,
                "state": "granted",
                "proof": "OTP-1",
                "notice_version_id": _notice(env).id,
            }
        )
    return partner


def _dnd(env, msisdn):
    return env["fix.dnd.registry"].create({"msisdn": msisdn, "source": "btrc_feed"})


def _campaign(env, user, tag, channel="sms", **vals):
    vals.setdefault("start_date", "2026-11-01")
    vals.setdefault("end_date", "2026-11-30")
    return (
        env["fix.campaign"]
        .with_user(user)
        .create(
            {
                "name": "M35P2 %s" % tag,
                "channel": channel,
                "budget": 1000.0,
                "target_audience_type": "custom_domain",
                "audience_domain": "[('name', '=like', '%s %%')]" % tag,
                **vals,
            }
        )
    )


def _audience_journey(env, user, campaign, body="Offer for {{name}}"):
    """A campaign-audience journey with one marketing send step."""
    journey = (
        env["fix.campaign.journey"]
        .with_user(user)
        .create(
            {
                "name": "Launch journey %s" % campaign.name,
                "campaign_id": campaign.id,
                "journey_kind": "campaign_audience",
            }
        )
    )
    env["fix.campaign.journey.step"].with_user(user).create(
        {
            "journey_id": journey.id,
            "sequence": 10,
            "name": "Offer SMS",
            "step_type": "send",
            "channel": "sms",
            "body": body,
        }
    )
    return journey


def _launch(campaign, user):
    with freeze_time(IN_WINDOW):
        campaign.with_user(user).action_scrub_dnd()
        campaign.with_user(user).action_launch()


# ==========================================================================
# 1. DND is enforced, not counted (G-M35-4)
# ==========================================================================
class TestDndEnforced:
    def test_a_dnd_party_is_scrubbed_out_and_never_receives_the_campaign(self, env, marketer):
        tag = "DNDA"
        keep = _party(env, tag, "Keep", "01711555000")
        listed = _party(env, tag, "Listed", "+880 1711-555001")
        _dnd(env, "01711555001")  # stored in the registry's own form
        campaign = _campaign(env, marketer, tag)
        with freeze_time(IN_WINDOW):
            campaign.with_user(marketer).action_scrub_dnd()
        assert campaign.dnd_excluded_count == 1
        assert campaign.dnd_excluded_partner_ids == listed
        with freeze_time(IN_WINDOW):
            campaign.with_user(marketer).action_launch()
        assert campaign.state == "running"
        assert campaign.recipient_ids == keep, "the DND party must leave the recipient list"
        assert campaign.dnd_excluded_partner_ids == listed
        assert campaign.excluded_no_consent_count == 0, "DND is not a consent exclusion"

    def test_launch_rechecks_the_registry_after_the_scrub(self, env, marketer):
        tag = "DNDB"
        keep = _party(env, tag, "Keep", "01711555010")
        late = _party(env, tag, "Late", "01711555011")
        campaign = _campaign(env, marketer, tag)
        with freeze_time(IN_WINDOW):
            campaign.with_user(marketer).action_scrub_dnd()
            assert campaign.dnd_excluded_count == 0
            _dnd(env, "8801711555011")  # listed between scrub and launch
            campaign.with_user(marketer).action_launch()
        assert campaign.recipient_ids == keep
        assert late in campaign.dnd_excluded_partner_ids

    def test_an_audience_entirely_on_dnd_launches_nothing(self, env, marketer):
        tag = "DNDC"
        _party(env, tag, "Only", "01711555020")
        _dnd(env, "01711555020")
        campaign = _campaign(env, marketer, tag)
        with freeze_time(IN_WINDOW):
            campaign.with_user(marketer).action_scrub_dnd()
            with pytest.raises(UserError, match="Do-Not-Disturb"):
                campaign.with_user(marketer).action_launch()
        assert campaign.state == "draft"

    def test_the_scrub_evidence_cannot_be_written_by_hand(self, env, marketer):
        tag = "DNDD"
        listed = _party(env, tag, "Listed", "01711555030")
        campaign = _campaign(env, marketer, tag)
        with pytest.raises(UserError, match="cannot be set directly"):
            campaign.with_user(marketer).write({"dnd_excluded_partner_ids": [(6, 0, [listed.id])]})
        with pytest.raises(UserError, match="cannot be set directly"):
            campaign.with_user(marketer).write({"dnd_scrubbed_at": "2026-11-03 04:00:00"})

    def test_a_dnd_party_is_not_enrolled_by_a_segment_journey(self, env, marketer):
        tag = "DNDE"
        keep = _party(env, tag, "Keep", "01711555040")
        listed = _party(env, tag, "Listed", "01711555041")
        _dnd(env, "01711555041")
        campaign = _campaign(env, marketer, tag)
        _launch(campaign, marketer)
        segment = env["fix.segment"].create({"code": "M35P2DNDE", "name": "DND segment"})
        segment.action_add_members([keep.id, listed.id])
        journey = (
            env["fix.campaign.journey"]
            .with_user(marketer)
            .create(
                {
                    "name": "Segment DND",
                    "campaign_id": campaign.id,
                    "journey_kind": "segment_scheduled",
                    "segment_id": segment.id,
                }
            )
        )
        env["fix.campaign.journey.step"].with_user(marketer).create(
            {"journey_id": journey.id, "sequence": 10, "name": "Exit", "step_type": "exit"}
        )
        journey.with_user(marketer).action_activate()
        assert journey.member_ids.mapped("partner_id") == keep

    def test_the_dnd_channels_switch_narrows_the_scope(self, env, marketer):
        tag = "DNDF"
        listed = _party(env, tag, "Listed", "01711555050", channel="email")
        listed.email = "listed@example.com"
        _dnd(env, "01711555050")
        campaign = _campaign(env, marketer, tag, channel="email")
        assert not campaign._dnd_reachable(listed), "fail-closed default: e-mail is bound"
        env["ir.config_parameter"].set_param("cd_campaign.dnd_channels", "sms")
        assert campaign._dnd_reachable(listed) == listed

    def test_a_running_campaign_is_not_re_scrubbed(self, env, marketer):
        tag = "DNDG"
        _party(env, tag, "Keep", "01711555060")
        campaign = _campaign(env, marketer, tag)
        _launch(campaign, marketer)
        with pytest.raises(UserError, match="before launch"):
            campaign.with_user(marketer).action_scrub_dnd()


# ==========================================================================
# 2. Pausing a campaign pauses its journeys; resume resumes them (G-M35-5)
# 5. Launch starts sending through the campaign-audience journey (G-M35-9)
# ==========================================================================
class TestPauseAndLaunchSending:
    def test_launch_enrols_the_scrubbed_recipients_and_sends(self, env, marketer):
        tag = "SEND"
        keep = _party(env, tag, "Keep", "01711556000")
        _party(env, tag, "Listed", "01711556001")
        _dnd(env, "01711556001")
        campaign = _campaign(env, marketer, tag)
        journey = _audience_journey(env, marketer, campaign)
        _launch(campaign, marketer)
        assert journey.state == "active", "launch activates the campaign's journeys"
        assert journey.member_ids.mapped("partner_id") == keep
        with freeze_time(IN_WINDOW):
            env["fix.campaign.journey"].cron_advance_journeys()
        member = journey.member_ids
        member.invalidate_recordset()
        assert member.delivery_ids, "launch must lead to a real S1 delivery row"
        assert member.delivery_ids[0].purpose == "marketing"

    def test_a_campaign_with_no_journey_says_it_sends_nothing(self, env, marketer):
        tag = "NOJ"
        _party(env, tag, "Keep", "01711556010")
        campaign = _campaign(env, marketer, tag)
        _launch(campaign, marketer)
        assert any("nothing is sent" in (m.body or "") for m in campaign.message_ids)

    def test_pause_stops_the_journey_and_resume_restarts_it(self, env, marketer):
        tag = "PAUSE"
        _party(env, tag, "Keep", "01711556020")
        campaign = _campaign(env, marketer, tag)
        journey = _audience_journey(env, marketer, campaign)
        _launch(campaign, marketer)
        campaign.with_user(marketer).action_pause()
        assert (journey.state, journey.paused_by_campaign) == ("paused", True)
        with freeze_time(IN_WINDOW):
            env["fix.campaign.journey"].cron_advance_journeys()
        assert not journey.member_ids.delivery_ids, "a paused campaign sends nothing"

        # The journey cannot be restarted around the paused campaign, by
        # action or by a direct write.
        with pytest.raises(UserError, match="Resume the campaign"):
            journey.with_user(marketer).action_resume_journey()
        with pytest.raises(UserError, match="cannot be set directly"):
            journey.with_user(marketer).write({"state": "active"})

        campaign.with_user(marketer).action_resume()
        assert (journey.state, journey.paused_by_campaign) == ("active", False)
        with freeze_time(IN_WINDOW):
            env["fix.campaign.journey"].cron_advance_journeys()
        journey.member_ids.invalidate_recordset()
        assert journey.member_ids.delivery_ids

    def test_resume_does_not_restart_a_journey_the_marketer_paused(self, env, marketer):
        tag = "PAUSE2"
        _party(env, tag, "Keep", "01711556030")
        campaign = _campaign(env, marketer, tag)
        journey = _audience_journey(env, marketer, campaign)
        _launch(campaign, marketer)
        journey.with_user(marketer).action_pause_journey()
        campaign.with_user(marketer).action_pause()
        campaign.with_user(marketer).action_resume()
        assert journey.state == "paused"

    def test_completing_a_campaign_stops_its_journeys(self, env, marketer):
        tag = "DONE"
        _party(env, tag, "Keep", "01711556040")
        campaign = _campaign(env, marketer, tag)
        journey = _audience_journey(env, marketer, campaign)
        _launch(campaign, marketer)
        campaign.with_user(marketer).action_complete()
        assert (journey.state, journey.paused_by_campaign) == ("paused", False)
        with pytest.raises(UserError, match="Resume the campaign"):
            journey.with_user(marketer).action_resume_journey()

    def test_a_journey_cannot_be_activated_by_a_state_write(self, env, marketer):
        tag = "JWRITE"
        campaign = _campaign(env, marketer, tag)
        journey = _audience_journey(env, marketer, campaign)
        with pytest.raises(UserError, match="cannot be set directly"):
            journey.with_user(marketer).write({"state": "active"})


# ==========================================================================
# 3. Purpose is bound to the template, not chosen per step (G-M35-6)
# ==========================================================================
class TestPurposeBoundToTemplate:
    @pytest.fixture
    def journey(self, env, marketer):
        campaign = _campaign(env, marketer, "PURP")
        return _audience_journey(env, marketer, campaign)

    def _template(self, env, consent_class):
        return env["fix.cc.notif.template"].create(
            {
                "name": "M35P2 %s" % consent_class,
                "channel": "sms",
                "body": "Your device is ready, {{name}}.",
                "consent_class": consent_class,
            }
        )

    def _step(self, env, user, journey, seq, **vals):
        return (
            env["fix.campaign.journey.step"]
            .with_user(user)
            .create(
                {
                    "journey_id": journey.id,
                    "sequence": seq,
                    "name": "Step %d" % seq,
                    "step_type": "send",
                    "channel": "sms",
                    **vals,
                }
            )
        )

    def test_marketing_copy_cannot_ride_service_updates(self, env, marketer, journey):
        # The step no longer chooses: a purpose sent with the step is not kept.
        step = self._step(
            env, marketer, journey, 20, body="50% off AC service!", purpose="service_updates"
        )
        step.invalidate_recordset()
        assert step.purpose == "marketing"
        with pytest.raises(ValidationError, match="marketing copy is always sent as marketing"):
            step.with_user(marketer).write({"purpose": "service_updates"})

    def test_the_template_decides(self, env, marketer, journey):
        transactional = self._template(env, "transactional")
        marketing = self._template(env, "marketing")
        service = self._step(env, marketer, journey, 20, template_id=transactional.id)
        promo = self._step(env, marketer, journey, 30, template_id=marketing.id)
        # A transactional template with authored copy on top is marketing.
        edited = self._step(
            env, marketer, journey, 40, template_id=transactional.id, body="Eid sale today!"
        )
        assert (service.purpose, promo.purpose, edited.purpose) == (
            "service_updates",
            "marketing",
            "marketing",
        )

    def test_the_send_uses_the_bound_purpose_not_the_stored_one(self, env, marketer):
        tag = "PURPRUN"
        _party(env, tag, "Keep", "01711557000")
        campaign = _campaign(env, marketer, tag)
        journey = _audience_journey(env, marketer, campaign, body="Big Eid offer")
        step = journey.step_ids
        # Even a value forced past the ORM is not what the engine sends with.
        env.cr.execute(
            "UPDATE fix_campaign_journey_step SET purpose = 'service_updates' WHERE id = %s",
            (step.id,),
        )
        step.invalidate_recordset()
        _launch(campaign, marketer)
        with freeze_time(IN_WINDOW):
            env["fix.campaign.journey"].cron_advance_journeys()
        journey.member_ids.invalidate_recordset()
        assert journey.member_ids.delivery_ids.purpose == "marketing"


# ==========================================================================
# 4. Creative approval gate through the M63 engine (G-M35-10)
# ==========================================================================
class TestCreativeApproval:
    @pytest.fixture
    def approver(self, make_user):
        return make_user(T2)

    def _creative(self, env, user, campaign, **vals):
        return (
            env["fix.campaign.creative"]
            .with_user(user)
            .create(
                {
                    "name": "Eid banner",
                    "campaign_id": campaign.id,
                    "asset_type": "image",
                    "reference": "s3://m35/eid-banner-v1.png",
                    # capture pass 2: BRU-MKT-10 needs the Bengali version and
                    # FR-MKT-024 an expiry before content is approved
                    "reference_bn": "s3://m35/eid-banner-v1-bn.png",
                    "expires_on": "2099-12-31",
                    **vals,
                }
            )
        )

    def test_approval_cannot_be_typed_or_pressed_directly(self, env, marketer):
        campaign = _campaign(env, marketer, "CRA", channel="social")
        creative = self._creative(env, marketer, campaign)
        with pytest.raises(UserError, match="cannot be set directly"):
            creative.with_user(marketer).write({"state": "approved"})
        with pytest.raises(UserError, match="approver's inbox"):
            creative.with_user(marketer).action_approve()
        assert creative.state == "draft"

    def test_launch_waits_for_the_approver(self, env, marketer, approver):
        campaign = _campaign(env, marketer, "CRB", channel="social")
        creative = self._creative(env, marketer, campaign)
        with pytest.raises(UserError, match="not approved yet"):
            campaign.with_user(marketer).action_launch()
        creative.with_user(marketer).action_request_approval(justification="Eid hero banner")
        assert creative.approval_state == "pending"
        assert not inbox_task(creative, marketer), "the maker is never routed own content"
        with pytest.raises(UserError, match="not approved yet"):
            campaign.with_user(marketer).action_launch()
        approve_via_inbox(creative, approver, requester=marketer)
        assert (creative.state, creative.approval_state) == ("approved", "approved")
        assert creative.approved_by_id == approver
        campaign.with_user(marketer).action_launch()
        assert campaign.state == "running"

    def test_an_approved_creative_is_withdrawn_before_it_is_edited(self, env, marketer, approver):
        campaign = _campaign(env, marketer, "CRC", channel="social")
        creative = self._creative(env, marketer, campaign)
        approve_via_inbox(creative, approver, requester=marketer)
        with pytest.raises(UserError, match="Withdraw it"):
            creative.with_user(marketer).write({"reference": "s3://m35/other.png"})
        assert "reference" in creative.with_user(marketer)._fix_form_locked_fields()
        creative.with_user(marketer).action_withdraw()
        assert (creative.state, creative.approval_state) == ("draft", "none")
        assert not creative.approved_by_id
        creative.with_user(marketer).write({"reference": "s3://m35/eid-banner-v2.png"})
        with pytest.raises(UserError, match="not approved yet"):
            campaign.with_user(marketer).action_launch()

    def test_withdrawing_live_content_pauses_the_campaign_until_reapproved(
        self, env, marketer, approver
    ):
        """A03 audit W7: a running campaign kept sending a withdrawn creative,
        and Resume did not look at the creatives at all."""
        campaign = _campaign(env, marketer, "CRW", channel="social")
        creative = self._creative(env, marketer, campaign)
        approve_via_inbox(creative, approver, requester=marketer)
        campaign.with_user(marketer).action_launch()
        assert campaign.state == "running"
        creative.with_user(marketer).action_withdraw()
        assert campaign.state == "paused"
        with pytest.raises(UserError, match="not approved yet"):
            campaign.with_user(marketer).action_resume()
        assert campaign.state == "paused"
        creative.with_user(marketer).write({"reference": "s3://m35/eid-banner-v2.png"})
        approve_via_inbox(creative, approver, requester=marketer)
        campaign.with_user(marketer).action_resume()
        assert campaign.state == "running"

    def test_pending_content_is_frozen_and_rejection_returns_it(self, env, marketer, approver):
        campaign = _campaign(env, marketer, "CRD", channel="social")
        creative = self._creative(env, marketer, campaign)
        creative.with_user(marketer).action_request_approval()
        with pytest.raises(UserError, match="awaiting approval"):
            creative.with_user(marketer).write({"name": "Swapped after submit"})
        task = inbox_task(creative, approver)
        with pytest.raises(UserError, match="State why"):
            task.with_user(approver).action_reject(comment="")
        task.with_user(approver).action_reject(comment="Logo is off-brand")
        assert (creative.state, creative.approval_state) == ("draft", "rejected")
        creative.with_user(marketer).write({"reference": "s3://m35/eid-banner-v3.png"})

    def test_a_creative_without_an_asset_cannot_be_submitted(self, env, marketer):
        campaign = _campaign(env, marketer, "CRE", channel="social")
        creative = self._creative(env, marketer, campaign, reference=False)
        with pytest.raises(UserError, match="no asset reference"):
            creative.with_user(marketer).action_request_approval()

    def test_a_tier2_maker_cannot_approve_own_creative(self, env, make_user):
        maker, other = make_user(T2), make_user(T2)
        campaign = _campaign(env, maker, "CRF", channel="social")
        creative = self._creative(env, maker, campaign)
        creative.with_user(maker).action_request_approval()
        assert not inbox_task(creative, maker)
        assert inbox_task(creative, other)

    def test_retired_creatives_do_not_block_and_the_switch_requires_one(self, env, marketer):
        campaign = _campaign(env, marketer, "CRG", channel="social")
        creative = self._creative(env, marketer, campaign)
        creative.with_user(marketer).action_retire()
        env["ir.config_parameter"].set_param("cd_campaign.launch_requires_approved_creative", "1")
        with pytest.raises(UserError, match="no approved creative"):
            campaign.with_user(marketer).action_launch()
        env["ir.config_parameter"].set_param("cd_campaign.launch_requires_approved_creative", "0")
        campaign.with_user(marketer).action_launch()
        assert campaign.state == "running"
        creative.with_user(marketer).action_reset_to_draft()
        assert creative.state == "draft"


# ==========================================================================
# 5b. Trigger journeys enrol through R8 consumers (G-M35-8)
# ==========================================================================
class TestTriggerJourneys:
    def _trigger_journey(self, env, user, campaign, event="party_role_added", **trigger_vals):
        trigger = (
            env["fix.campaign.trigger"]
            .with_user(user)
            .create({"name": "On role", "campaign_id": campaign.id, "event": event, **trigger_vals})
        )
        journey = (
            env["fix.campaign.journey"]
            .with_user(user)
            .create(
                {
                    "name": "Trigger journey",
                    "campaign_id": campaign.id,
                    "journey_kind": "trigger_immediate",
                    "trigger_id": trigger.id,
                }
            )
        )
        env["fix.campaign.journey.step"].with_user(user).create(
            {"journey_id": journey.id, "sequence": 10, "name": "Exit", "step_type": "exit"}
        )
        return trigger, journey

    def _relay_only(self, env, event_ids):
        """Relay just these events: every other pending row is marked done."""
        env.cr.execute(
            "UPDATE fix_event_outbox SET relayed_at = now() AT TIME ZONE 'UTC' "
            "WHERE relayed_at IS NULL AND event_id NOT IN %s",
            (tuple(event_ids),),
        )
        env["fix.event.consumer"].search([]).write({"active_from": "2020-01-01 00:00:00"})
        return env["fix.event.outbox"].cron_relay()

    def test_the_declared_trigger_events_have_consumers(self, env):
        Consumer = env["fix.event.consumer"]
        for event_type in (
            "party.role_added",
            "loyalty.tier_upgraded",
            "consent.captured",
            "survey.detractor_flagged",
        ):
            assert Consumer.search_count(
                [
                    ("event_type", "=", event_type),
                    ("model", "=", "fix.campaign.journey"),
                    ("method", "=", "consume_journey_trigger"),
                ]
            ), event_type

    def test_an_event_enrols_once_through_the_relay(self, env, marketer):
        tag = "TRIG"
        party = _party(env, tag, "Joiner", "01711558000")
        campaign = _campaign(env, marketer, tag)
        _launch(campaign, marketer)
        trigger, journey = self._trigger_journey(env, marketer, campaign)
        assert trigger.consumer_registered
        assert journey.state == "draft", "added after launch: activated by hand"
        journey.with_user(marketer).action_activate()
        event_id = publish(
            env,
            "party.role_added",
            "res.partner",
            party.id,
            {"partner_id": party.id, "role_type": "customer", "role_status": "active"},
        )
        self._relay_only(env, [event_id])
        assert journey.member_ids.mapped("partner_id") == party
        # A redelivered event (or a replayed relay) enrols nobody twice.
        outbox = env["fix.event.outbox"].search([("event_id", "=", event_id)])
        env["fix.campaign.journey"].consume_journey_trigger(outbox._relay_event_dict())
        journey.invalidate_recordset()
        assert len(journey.member_ids) == 1

    def test_a_paused_campaign_admits_nobody(self, env, marketer):
        tag = "TRIGP"
        party = _party(env, tag, "Joiner", "01711558010")
        campaign = _campaign(env, marketer, tag)
        _launch(campaign, marketer)
        _trigger, journey = self._trigger_journey(env, marketer, campaign)
        journey.with_user(marketer).action_activate()
        campaign.with_user(marketer).action_pause()
        result = env["fix.campaign.journey"].consume_journey_trigger(
            {
                "event_id": "m35-p2-paused",
                "event_type": "party.role_added",
                "aggregate": "res.partner",
                "aggregate_id": party.id,
                "payload": {"partner_id": party.id},
            }
        )
        assert result["enrolled"] == 0
        assert not journey.member_ids

    def test_a_custom_event_type_registers_its_consumer(self, env, marketer):
        campaign = _campaign(env, marketer, "TRIGC", channel="social")
        trigger = (
            env["fix.campaign.trigger"]
            .with_user(marketer)
            .create({"name": "Custom", "campaign_id": campaign.id, "event": "inactivity"})
        )
        trigger.with_user(marketer).write({"outbox_event_type": "warranty.expiring_soon"})
        consumer = env["fix.event.consumer"].search([("event_type", "=", "warranty.expiring_soon")])
        assert (consumer.model, consumer.method) == (
            "fix.campaign.journey",
            "consume_journey_trigger",
        )


# ==========================================================================
# 6. Cron 36 releases each held campaign in its own savepoint (G-M35-7)
# ==========================================================================
class TestCurfewReleaseCron:
    def test_one_bad_campaign_does_not_hold_back_the_rest(self, env, marketer):
        good_p = _party(env, "CURA", "Keep", "01711559000")
        _party(env, "CURB", "Keep", "01711559001")
        bad_p = _party(env, "CURC", "Keep", "01711559002")
        good = _campaign(env, marketer, "CURA")
        stale = _campaign(env, marketer, "CURB")
        bad = _campaign(env, marketer, "CURC")
        # The stale one is scrubbed 21h before an out-of-hours launch, so its
        # scrub is 28h old when the window opens.
        with freeze_time("2026-11-02 00:00:00"):
            stale.with_user(marketer).action_scrub_dnd()
        # 03:00 BST: all three are held until 08:00 BST (02:00 UTC).
        with freeze_time("2026-11-02 21:00:00"):
            for campaign in (good, bad):
                campaign.with_user(marketer).action_scrub_dnd()
            for campaign in (good, stale, bad):
                campaign.with_user(marketer).action_launch()
        assert {good.state, stale.state, bad.state} == {"draft"}
        assert good.dispatch_hold_until and stale.dispatch_hold_until and bad.dispatch_hold_until
        # The bad one's only consent is withdrawn while it waits.
        env["fix.consent"].search([("partner_id", "=", bad_p.id)]).action_withdraw()
        with freeze_time(IN_WINDOW):
            result = env["fix.campaign"].cron_release_curfew_holds()
        assert result == {"released": 2, "failed": 1}
        assert (good.state, stale.state, bad.state) == ("running", "running", "draft")
        assert good.recipient_ids == good_p
        assert not bad.dispatch_hold_until, "a failed release stops retrying"
        assert any("could not be launched" in (m.body or "") for m in bad.message_ids)
        assert str(stale.dnd_scrubbed_at).startswith("2026-11-03 04:00"), "re-scrubbed"


# ==========================================================================
# Also: auto-complete at end date, budget versus actual, cron 52 harvest
# ==========================================================================
class TestCloseAndReconcile:
    def test_campaigns_past_their_end_date_complete(self, env, marketer):
        _party(env, "ENDA", "Keep", "01711560000")
        ended = _campaign(env, marketer, "ENDA", start_date="2026-10-01", end_date="2026-10-31")
        journey = _audience_journey(env, marketer, ended)
        current = _campaign(env, marketer, "ENDB", channel="social")
        _launch(ended, marketer)
        current.with_user(marketer).action_launch()
        with freeze_time(IN_WINDOW):
            result = env["fix.campaign"].cron_complete_ended_campaigns()
        assert result["completed"] >= 1
        assert (ended.state, current.state) == ("completed", "running")
        assert journey.state == "paused"
        assert env.ref("cd_campaign.ir_cron_campaign_complete_ended").active

    def test_budget_versus_recorded_spend(self, env, marketer):
        campaign = _campaign(env, marketer, "BVA", channel="social", budget=10000.0)
        offer = env["fix.campaign.offer"].create(
            {"name": "BVA offer", "campaign_id": campaign.id, "offer_type": "fixed", "value": 500}
        )
        campaign.with_user(marketer).action_launch()
        offer.action_record_redemption(False, 2500.0)
        campaign.invalidate_recordset()
        assert campaign.actual_spend == 2500.0
        assert campaign.budget_variance == 7500.0
        assert campaign.budget_utilisation_pct == 25.0

    def test_the_touch_harvest_survives_one_bad_row(self, env, marketer):
        tag = "HARV"
        _party(env, tag, "Keep", "01711561000")
        _party(env, tag, "Other", "01711561001")
        campaign = _campaign(env, marketer, tag)
        _audience_journey(env, marketer, campaign)
        _launch(campaign, marketer)
        with freeze_time(IN_WINDOW):
            env["fix.campaign.journey"].cron_advance_journeys()
        rows = campaign.journey_ids.member_ids.delivery_ids
        assert len(rows) == 2
        rows._guarded().write({"state": "sent", "sent_at": "2026-11-03 04:00:00"})
        Touch = type(env["fix.campaign.touch"])
        real = Touch.record
        calls = []

        def flaky(self, *args, **kwargs):
            calls.append(1)
            if len(calls) == 1:
                raise ValueError("simulated unrecordable row")
            return real(self, *args, **kwargs)

        with freeze_time(IN_WINDOW), patch.object(Touch, "record", flaky):
            result = env["fix.campaign.touch"].cron_harvest_from_delivery_log()
        assert result["failed"] == 1 and result["touches"] >= 1


# ==========================================================================
# P03: every new user-facing action is whitelisted AND has a button
# ==========================================================================
def test_p03_surfaces_and_buttons_match():
    from odoo.addons.cd_p03_portal.controllers.a03.m35 import SURFACES

    expected = {
        "fix.campaign": {"action_scrub_dnd"},
        "fix.campaign.journey": {
            "action_activate",
            "action_pause_journey",
            "action_resume_journey",
        },
        "fix.campaign.creative": {
            "action_request_approval",
            "action_recall_approval",
            "action_withdraw",
            "action_retire",
            "action_reset_to_draft",
        },
    }
    js = M35_JS.read_text(encoding="utf-8")
    for model, actions in expected.items():
        assert actions <= SURFACES[model]["actions"], model
        for action in actions:
            assert "m: '%s'" % action in js, action
    # The approve step is the inbox's, never a workspace button.
    assert "action_approve" not in SURFACES["fix.campaign.creative"]["actions"]
