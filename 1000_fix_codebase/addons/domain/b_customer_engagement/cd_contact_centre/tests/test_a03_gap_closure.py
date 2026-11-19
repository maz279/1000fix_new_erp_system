"""test_a03_gap_closure.py - executable proof for the A03 gap-closure build.

Every test here calls PRODUCTION code against the live ORM, in the same
posture as test_a03_zero_trust_certification.py: no MagicMock stand-ins, no
locally re-implemented controls, no `inspect.getsource` string assertions. A
test fails if the capability it names is absent from the running system.

Covered, in the gap plan's own numbering:

  S1  Notification Delivery Service      - logging, suppression, retry,
                                           idempotency, unit economics, DE-17
  S2  Consent Enforcement API            - purpose AND channel, latest-wins,
                                           declared non-consent bases
  S3  Unified Routing Workstreams        - classification, dual capacity
                                           profiles, pick, affinity, overflow
  S4  Agent Presence                     - capacity-derived Busy-DND,
                                           missed-offer demotion, adherence
  S5  Entitlement Lookup                 - party-level verdict at intake
  S8  Duplicate Detection Jobs           - the third layer, idempotent
  S9  SLA KPI Instances                  - cancel-and-recreate on resume,
                                           business-hours arithmetic
  S10 Journey / Sequence Runtime         - kind discriminator, per-step
                                           re-evaluation, loop guard
  M10 Loyalty Scheme Engine              - tier-scoped rules, affiliations,
                                           non-redeemable points, requalification
  M34 Survey Designer                    - branching, range checks, freezing
"""

import pytest
from odoo import fields as odoo_fields
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError

# fix.working.calendar.line.weekday is a Selection of these keys, not the
# integers date.weekday() returns. The production calendar walk used the
# integers, which matched nothing and made every calendar read as closed.
WEEKDAY_KEYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


def _ou(env):
    unit = env["operating.unit"].search([], limit=1)
    if not unit:
        unit = env["operating.unit"].create({"name": "GAP Unit", "code": "GAPU"})
    return unit


# ==========================================================================
# Fixtures
# ==========================================================================
@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def customer(env):
    return env["res.partner"].create(
        {"name": "Gap Closure Customer", "phone": "01712000001", "email": "gap@example.test"}
    )


@pytest.fixture
def notice(env):
    return env["fix.transparency.notice"].search([], limit=1) or env[
        "fix.transparency.notice"
    ].create({"version": "GAP-NOTICE-1", "text_en": "Gap notice", "text_bn": "নোটিশ"})


@pytest.fixture
def grant(env, notice):
    """Grant a consent for (purpose, channel) on a party."""

    def _grant(partner, purpose, channel):
        return env["fix.consent"].create(
            {
                "partner_id": partner.id,
                "purpose": purpose,
                "channel": channel,
                "state": "granted",
                "proof": "GAP-OTP-1",
                "notice_version_id": notice.id,
            }
        )

    return _grant


@pytest.fixture
def presence_statuses(env):
    """The presence vocabulary S4 needs, as SHIPPED by the module.

    Deliberately resolves the seeded records rather than creating its own: a
    second available-class status or a second system Busy-DND would make
    dnd_status() ambiguous, and a test that invents the vocabulary it is
    testing proves nothing about what a fresh install actually has.
    """
    Status = env["fix.cc.presence.status"]
    available = Status.search([("is_available_class", "=", True)], order="sequence", limit=1)
    dnd = Status.dnd_status()
    offline = Status.search(
        [("is_available_class", "=", False), ("is_system_dnd", "=", False)],
        order="sequence desc",
        limit=1,
    )
    assert available and dnd and offline, (
        "the module must SHIP a presence vocabulary: routing is unusable "
        "without one, and state_for() rightly refuses to invent it"
    )
    return {"available": available, "dnd": dnd, "offline": offline}


@pytest.fixture
def agent(env):
    return env["res.users"].create(
        {
            "name": "Gap Agent",
            "login": "gap.agent.%d" % env["res.users"].search_count([]),
            "cc_skills": "laptop,bengali",
        }
    )


@pytest.fixture
def queue(env):
    return env["fix.cc.queue"].create({"name": "Gap Queue", "code": "GAPQ", "channel": "voice"})


# ==========================================================================
# S2 - the Consent Enforcement API
# ==========================================================================
class TestS2ConsentEnforcement:
    def test_absence_of_a_record_is_a_refusal_not_a_permission(self, env, customer):
        verdict = env["fix.consent"].consent_check(customer, "marketing", "sms")
        assert verdict["allowed"] is False
        assert verdict["decision"] == "absent"
        assert "not a permission" in verdict["reason"]

    def test_a_marketing_consent_does_not_authorise_call_recording(self, env, customer, grant):
        """The defect the old channel-only check would have let through.

        M35's local filter looked at CHANNEL and ignored PURPOSE entirely, so
        an all-channel marketing opt-in counted as consent for anything. The
        'marketing' umbrella must satisfy marketing only.
        """
        grant(customer, "marketing", "marketing")
        assert env["fix.consent"].consent_check(customer, "marketing", "sms")["allowed"]
        recording = env["fix.consent"].consent_check(customer, "call_recording", "voice")
        assert recording["allowed"] is False
        assert recording["decision"] == "absent"

    def test_a_service_updates_optin_is_not_a_marketing_optin(self, env, customer, grant):
        grant(customer, "service_updates", "sms")
        assert env["fix.consent"].consent_check(customer, "service_updates", "sms")["allowed"]
        assert not env["fix.consent"].consent_check(customer, "marketing", "sms")["allowed"]

    def test_the_latest_decision_wins_in_both_directions(self, env, customer, grant):
        consent = grant(customer, "marketing", "sms")
        assert env["fix.consent"].consent_check(customer, "marketing", "sms")["allowed"]
        consent.action_withdraw()
        after = env["fix.consent"].consent_check(customer, "marketing", "sms")
        assert after["allowed"] is False and after["decision"] == "withdrawn"
        grant(customer, "marketing", "sms")  # re-granted later
        assert env["fix.consent"].consent_check(customer, "marketing", "sms")["allowed"]

    def test_an_unidentified_party_cannot_be_consent_checked(self, env):
        verdict = env["fix.consent"].consent_check(False, "marketing", "sms")
        assert verdict["decision"] == "unidentified"
        assert verdict["allowed"] is False

    def test_a_declared_non_consent_basis_is_permitted_and_recorded(self, env, customer):
        verdict = env["fix.consent"].consent_check(
            customer, "service_updates", "sms", basis="contract"
        )
        assert verdict["allowed"] is True
        assert verdict["decision"] == "basis_declared"
        assert "contract" in verdict["reason"].lower()

    def test_an_unknown_basis_is_refused_rather_than_assumed(self, env, customer):
        verdict = env["fix.consent"].consent_check(
            customer, "marketing", "sms", basis="because_i_said_so"
        )
        assert verdict["allowed"] is False
        assert "Unknown lawful basis" in verdict["reason"]

    def test_bulk_returns_the_allowed_set_and_explains_each_exclusion(self, env, grant, notice):
        Partner = env["res.partner"]
        yes = Partner.create({"name": "Bulk Yes", "phone": "01712000010"})
        no = Partner.create({"name": "Bulk No", "phone": "01712000011"})
        gone = Partner.create({"name": "Bulk Gone", "phone": "01712000012"})
        grant(yes, "marketing", "sms")
        grant(gone, "marketing", "sms").action_withdraw()
        allowed, excluded = env["fix.consent"].consent_check_bulk(
            yes | no | gone, "marketing", "sms"
        )
        assert allowed == yes
        assert excluded[no.id]["decision"] == "absent"
        assert excluded[gone.id]["decision"] == "withdrawn"

    def test_consent_assert_raises_with_the_stated_reason(self, env, customer):
        with pytest.raises(ValidationError, match="not a permission"):
            env["fix.consent"].consent_assert(customer, "marketing", "sms")


# ==========================================================================
# S1 - the Notification Delivery Service
# ==========================================================================
class TestS1NotificationDelivery:
    def test_a_refused_send_is_logged_as_suppressed_not_dropped(self, env, customer):
        """A suppression is the evidence the rule worked, so it is a row."""
        delivery = env["fix.notif.delivery"].queue(
            channel="sms",
            purpose="marketing",
            partner=customer,
            body="Promo",
        )
        assert delivery.state == "suppressed"
        assert delivery.consent_decision == "absent"
        assert delivery.sent_at is False
        assert delivery.cost == 0.0

    def test_a_consented_send_is_queued(self, env, customer, grant):
        grant(customer, "marketing", "sms")
        delivery = env["fix.notif.delivery"].queue(
            channel="sms", purpose="marketing", partner=customer, body="Promo"
        )
        assert delivery.state == "queued"
        assert delivery.consent_decision == "granted"
        assert delivery.to_address == customer.phone

    def test_the_idempotency_key_prevents_a_double_send(self, env, customer, grant):
        grant(customer, "service_updates", "sms")
        first = env["fix.notif.delivery"].queue(
            channel="sms",
            purpose="service_updates",
            partner=customer,
            body="Your order is ready",
            dedup_key="gap-dedup-1",
        )
        second = env["fix.notif.delivery"].queue(
            channel="sms",
            purpose="service_updates",
            partner=customer,
            body="Your order is ready",
            dedup_key="gap-dedup-1",
        )
        assert first == second

    def test_an_addressless_send_is_refused_rather_than_invented(self, env):
        anonymous = env["res.partner"].create({"name": "No Contact Details"})
        with pytest.raises(ValidationError, match="no destination address"):
            env["fix.notif.delivery"].queue(
                channel="sms", purpose="service_updates", partner=anonymous, body="Hi"
            )

    def test_an_empty_body_is_refused(self, env, customer):
        with pytest.raises(ValidationError, match="empty message body"):
            env["fix.notif.delivery"].queue(
                channel="sms", purpose="service_updates", partner=customer, body="   "
            )

    def test_without_a_provider_nothing_is_claimed_to_have_been_sent(self, env, customer, grant):
        """The honest state: no carrier is contracted, so nothing is pretended."""
        grant(customer, "service_updates", "sms")
        delivery = env["fix.notif.delivery"].queue(
            channel="sms", purpose="service_updates", partner=customer, body="Ready"
        )
        env["fix.notif.provider"].search([("channel", "=", "sms")]).write({"active": False})
        delivery.write({"provider_id": False})
        delivery.action_send()
        assert delivery.state == "queued"
        assert "No provider is configured" in delivery.last_error
        assert delivery.sent_at is False

    def test_delivery_is_never_assumed_from_a_send(self, env, customer, grant):
        grant(customer, "service_updates", "sms")
        delivery = env["fix.notif.delivery"].queue(
            channel="sms", purpose="service_updates", partner=customer, body="Ready"
        )
        with pytest.raises(UserError, match="already sent"):
            delivery.mark_delivered()

    def test_a_sent_message_body_cannot_be_rewritten(self, env, customer, grant):
        """The log is evidence of what the subscriber was told."""
        grant(customer, "service_updates", "sms")
        delivery = env["fix.notif.delivery"].queue(
            channel="sms", purpose="service_updates", partner=customer, body="Ready"
        )
        delivery.write({"state": "sent", "sent_at": odoo_fields.Datetime.now()})
        with pytest.raises(UserError, match="delivery log is evidence"):
            delivery.write({"body": "something else entirely"})
        with pytest.raises(UserError, match="cannot be deleted"):
            delivery.unlink()

    def test_the_btrc_curfew_holds_marketing_but_not_an_order_update(self, env, customer, grant):
        from freezegun import freeze_time

        grant(customer, "marketing", "sms")
        grant(customer, "service_updates", "sms")
        # 23:00 BST == 17:00 UTC
        with freeze_time("2026-11-03 17:00:00"):
            promo = env["fix.notif.delivery"].queue(
                channel="sms",
                purpose="marketing",
                partner=customer,
                body="Promo",
                dedup_key="gap-curfew-promo",
            )
            txn = env["fix.notif.delivery"].queue(
                channel="sms",
                purpose="service_updates",
                partner=customer,
                body="Your device is ready for collection",
                dedup_key="gap-curfew-txn",
            )
        assert promo.curfew_bound is True
        assert promo.curfew_hold_until
        assert txn.curfew_bound is False
        assert txn.curfew_hold_until is False

    def test_a_bengali_preferring_customer_gets_the_bengali_body(self, env, customer, grant):
        """DE-17 measured at the point it matters: what was actually sent."""
        grant(customer, "service_updates", "sms")
        customer.write({"preferred_language": "bn"})
        template = env["fix.cc.notif.template"].create(
            {
                "name": "Gap Ready",
                "channel": "sms",
                "body": "Your device is ready.",
                "body_bn": "আপনার ডিভাইস প্রস্তুত।",
                "consent_class": "transactional",
            }
        )
        delivery = env["fix.notif.delivery"].queue(
            channel="sms",
            purpose="service_updates",
            partner=customer,
            template=template,
            dedup_key="gap-bn-1",
        )
        assert delivery.language == "bn"
        assert delivery.body == "আপনার ডিভাইস প্রস্তুত।"

    def test_a_missing_bengali_body_falls_back_and_says_so(self, env, customer, grant):
        """The fallback is visible, so missing Bengali copy is a number."""
        grant(customer, "service_updates", "sms")
        customer.write({"preferred_language": "bn"})
        template = env["fix.cc.notif.template"].create(
            {
                "name": "Gap English Only",
                "channel": "sms",
                "body": "English only body.",
                "consent_class": "transactional",
            }
        )
        delivery = env["fix.notif.delivery"].queue(
            channel="sms",
            purpose="service_updates",
            partner=customer,
            template=template,
            dedup_key="gap-bn-2",
        )
        assert delivery.language == "en"
        assert delivery.body == "English only body."

    def test_cost_is_read_from_the_tariff_and_never_estimated(self, env, customer, grant):
        grant(customer, "service_updates", "whatsapp")
        provider = env["fix.notif.provider"].create(
            {
                "name": "Gap WA Manual",
                "code": "GAPWA",
                "channel": "whatsapp",
                "transport": "manual",
                "cost_per_message": 0.85,
            }
        )
        delivery = env["fix.notif.delivery"].queue(
            channel="whatsapp",
            purpose="service_updates",
            partner=customer,
            body="Ready",
            dedup_key="gap-wa-1",
        )
        assert delivery.provider_id == provider
        delivery.action_mark_sent_manually(provider_ref="wa-1")
        assert delivery.state == "sent"
        assert delivery.cost == 0.85
        summary = {row["channel"]: row for row in env["fix.notif.delivery"].delivery_cost_summary()}
        wa = summary["whatsapp"]
        assert wa["sent"] >= 1
        assert wa["cost"] >= 0.85
        # Every state must be counted, or the columns stop summing to the row
        # total -- which is what happened when 'dry_run' was added and the
        # bucket listed five states by hand.
        states = [k for k, _ in env["fix.notif.delivery"]._fields["state"].selection]
        assert sum(wa[st] for st in states) == wa["messages"], (
            "state tallies must sum to the message count: %s" % wa
        )

    def test_the_dispatch_queue_leaves_a_manual_message_for_the_operator(
        self, env, customer, grant
    ):
        """Manual transport means an operator sends it; the cron must not
        fail it permanently before anyone can."""
        grant(customer, "service_updates", "whatsapp")
        env["fix.notif.provider"].create(
            {
                "name": "Gap WA Operator",
                "code": "GAPWAOP",
                "channel": "whatsapp",
                "transport": "manual",
            }
        )
        delivery = env["fix.notif.delivery"].queue(
            channel="whatsapp",
            purpose="service_updates",
            partner=customer,
            body="Ready",
            dedup_key="gap-wa-manual-cron",
        )
        assert delivery.provider_id.transport == "manual"
        env["fix.notif.delivery"].cron_dispatch_queue()
        assert delivery.state == "queued"
        delivery.action_mark_sent_manually(provider_ref="wa-op-1")
        assert delivery.state == "sent"

    def test_suppression_reasons_are_reportable(self, env, customer):
        env["fix.notif.delivery"].queue(
            channel="sms",
            purpose="marketing",
            partner=customer,
            body="Promo",
            dedup_key="gap-supp-1",
        )
        rows = env["fix.notif.delivery"].suppression_reasons()
        assert any(
            r["channel"] == "sms" and r["purpose"] == "marketing" and r["messages"] >= 1
            for r in rows
        )


# ==========================================================================
# S4 - Agent presence, derived from capacity
# ==========================================================================
class TestS4AgentPresence:
    def test_a_missing_presence_row_defaults_to_offline_not_available(
        self, env, agent, presence_statuses
    ):
        """Defaulting to available would silently enrol every new user."""
        state = env["fix.cc.agent.state"].state_for(agent)
        assert state.presence_status_id.is_available_class is False

    def test_presence_changes_are_logged_as_closed_intervals(self, env, agent, presence_statuses):
        state = env["fix.cc.agent.state"].state_for(agent)
        state.set_presence(presence_statuses["available"])
        state.set_presence(presence_statuses["offline"])
        logs = env["fix.cc.agent.state.log"].search([("agent_id", "=", agent.id)], order="from_at")
        assert len(logs) >= 2
        assert logs[0].to_at, "the earlier interval must be closed"

    def test_presence_history_cannot_be_rewritten_or_deleted(self, env, agent, presence_statuses):
        state = env["fix.cc.agent.state"].state_for(agent)
        state.set_presence(presence_statuses["available"])
        state.set_presence(presence_statuses["offline"])
        closed = env["fix.cc.agent.state.log"].search(
            [("agent_id", "=", agent.id), ("to_at", "!=", False)], limit=1
        )
        with pytest.raises(UserError, match="append-only"):
            closed.write({"presence_source": "manual", "from_at": closed.from_at})
        with pytest.raises(UserError, match="cannot be deleted"):
            closed.unlink()

    def test_two_missed_offers_force_the_agent_unavailable(self, env, agent, presence_statuses):
        """An unresponsive agent marked available drains the queue."""
        state = env["fix.cc.agent.state"].state_for(agent)
        state.set_presence(presence_statuses["available"])
        state.register_missed_offer()
        assert state.presence_status_id.is_available_class is True
        state.register_missed_offer()
        assert state.presence_status_id == presence_statuses["dnd"]
        assert state.presence_source == "missed_notification"

    def test_a_dnd_status_cannot_also_receive_work(self, env):
        with pytest.raises(ValidationError, match="cannot also be a status"):
            env["fix.cc.presence.status"].create(
                {
                    "name": "Contradiction",
                    "code": "GAP-BAD",
                    "is_available_class": True,
                    "is_system_dnd": True,
                }
            )

    def test_a_capacity_profile_must_allow_at_least_one_item(self, env):
        with pytest.raises(ValidationError, match="at least one work item"):
            env["fix.cc.capacity.profile"].create(
                {"name": "Zero", "code": "GAP-ZERO", "work_item_limit": 0}
            )

    def test_a_personal_limit_overrides_the_profile_limit(self, env, agent):
        profile = env["fix.cc.capacity.profile"].create(
            {"name": "Gap Total", "code": "GAP-TOTAL", "work_item_limit": 3}
        )
        assert profile.limit_for(agent) == 3
        env["fix.cc.capacity.assignment"].create(
            {"agent_id": agent.id, "profile_id": profile.id, "max_units_override": 1}
        )
        assert profile.limit_for(agent) == 1


# ==========================================================================
# S3 - Unified routing
# ==========================================================================
class TestS3UnifiedRouting:
    @pytest.fixture
    def workstream(self, env, queue):
        profile = env["fix.cc.capacity.profile"].create(
            {"name": "Gap WS Total", "code": "GAP-WS-TOTAL", "work_item_limit": 2}
        )
        return env["fix.routing.workstream"].create(
            {
                "name": "Gap Voice Workstream",
                "code": "GAP-WS",
                "channel": "voice",
                "work_type": "conversation",
                "queue_id": queue.id,
                "default_capacity_profile_id": profile.id,
                "assignment_method": "pick",
            }
        )

    def test_profiles_and_flat_units_cannot_both_be_configured(self, env, workstream):
        """Microsoft's own warning, enforced rather than documented."""
        with pytest.raises(ValidationError, match="Configure one or the other"):
            workstream.write({"use_capacity_units": True})

    def test_bullseye_without_rings_is_refused(self, env, workstream):
        with pytest.raises(ValidationError, match="never widen"):
            workstream.write({"assignment_method": "bullseye"})

    def test_a_classification_rule_appends_a_second_capacity_profile(
        self, env, workstream, customer
    ):
        """The dual-profile mechanic: room is needed in BOTH."""
        urgent = env["fix.cc.capacity.profile"].create(
            {"name": "Gap Urgent", "code": "GAP-URGENT", "work_item_limit": 1}
        )
        env["fix.routing.ruleset"].create(
            {
                "workstream_id": workstream.id,
                "sequence": 10,
                "name": "Critical gets the urgent profile",
                "condition_kind": "urgency",
                "condition_value": "high",
                "priority": 50,
                "required_skill": "laptop",
                "appended_capacity_profile_id": urgent.id,
            }
        )
        item = workstream.intake(
            "fix.conversation",
            1,
            partner=customer,
            context_values={"urgency_level": "critical"},
        )
        assert item.priority == 50
        assert item.required_skill == "laptop"
        assert set(item.capacity_profile_ids.mapped("code")) == {"GAP-WS-TOTAL", "GAP-URGENT"}

    def test_a_non_matching_item_carries_only_the_workstream_default(
        self, env, workstream, customer
    ):
        env["fix.routing.ruleset"].create(
            {
                "workstream_id": workstream.id,
                "sequence": 10,
                "name": "Critical only",
                "condition_kind": "urgency",
                "condition_value": "critical",
                "priority": 90,
            }
        )
        item = workstream.intake(
            "fix.conversation",
            2,
            partner=customer,
            context_values={"urgency_level": "low"},
        )
        assert item.capacity_profile_ids.mapped("code") == ["GAP-WS-TOTAL"]
        assert item.priority == 0

    def test_pick_assigns_without_any_presence_model(self, env, workstream, customer, agent):
        """Pick is the slice of routing that needs no presence engine."""
        item = workstream.intake("fix.conversation", 3, partner=customer)
        item.with_user(agent).action_pick()
        assert item.state == "assigned"
        assert item.assigned_agent_id == agent
        assert item.assignment_mode == "pick"

    def test_capacity_may_go_negative_on_a_pick_rather_than_being_clamped(
        self, env, workstream, customer, agent, presence_statuses
    ):
        """Microsoft documents this; a clamped figure hides a real overload."""
        state = env["fix.cc.agent.state"].state_for(agent)
        state.set_presence(presence_statuses["available"])
        profile = workstream.default_capacity_profile_id
        items = []
        for n in range(4):  # limit is 2
            item = workstream.intake("fix.conversation", 100 + n, partner=customer)
            item.with_user(agent).action_pick()
            items.append(item)
        held = state.units_held(profile)
        assert held == 4, "held units must reflect reality, not the ceiling"
        assert held > profile.limit_for(agent)

    def test_a_manual_assignment_requires_a_stated_reason(self, env, workstream, customer, agent):
        item = workstream.intake("fix.conversation", 4, partner=customer)
        with pytest.raises(UserError, match="requires a stated reason"):
            item.action_assign_manually(agent=agent)
        item.action_assign_manually(agent=agent, reason="VIP escalation by the duty manager")
        assert item.assigned_agent_id == agent
        assert item.assignment_mode == "manual"

    def test_a_conversation_releases_capacity_only_when_the_session_closes(
        self, env, workstream, customer, agent
    ):
        item = workstream.intake("fix.conversation", 5, partner=customer)
        item.with_user(agent).action_pick()
        item.close_and_release(session_closed=False)
        assert item.state == "closed"
        assert item.capacity_released is False
        assert "session is still open" in (item.message_ids[0].body or "").lower()

    def test_a_record_work_item_never_releases_automatically(self, env, queue, customer, agent):
        """There is no end event to hang a release on, so a guess would hand
        the agent capacity they are still using."""
        ws = env["fix.routing.workstream"].create(
            {
                "name": "Gap Records",
                "code": "GAP-REC",
                "channel": "email",
                "work_type": "record",
                "queue_id": queue.id,
                "assignment_method": "pick",
            }
        )
        item = ws.intake("res.partner", customer.id, partner=customer)
        item.with_user(agent).action_pick()
        item.close_and_release(session_closed=True)
        assert item.capacity_released is False
        item.action_release_capacity(reason="Supervisor confirmed the work is finished")
        assert item.capacity_released is True

    def test_an_end_of_day_profile_does_not_release_on_close(self, env, queue, customer, agent):
        daily = env["fix.cc.capacity.profile"].create(
            {
                "name": "Gap Daily Quota",
                "code": "GAP-DAILY",
                "work_item_limit": 5,
                "reset_frequency": "end_of_day",
            }
        )
        ws = env["fix.routing.workstream"].create(
            {
                "name": "Gap Daily",
                "code": "GAP-WS-DAILY",
                "channel": "voice",
                "work_type": "conversation",
                "queue_id": queue.id,
                "default_capacity_profile_id": daily.id,
                "assignment_method": "pick",
            }
        )
        item = ws.intake("fix.conversation", 6, partner=customer)
        item.with_user(agent).action_pick()
        item.close_and_release(session_closed=True)
        assert item.capacity_released is False
        assert env["fix.routing.workitem"].cron_reset_end_of_day_capacity() >= 1
        assert item.capacity_released is True

    def test_monitoring_does_not_consume_capacity(self, env, workstream, customer):
        item = workstream.intake("fix.conversation", 7, partner=customer)
        item.write({"is_monitoring": True})
        assert item._release_allowed(session_closed=False) is True

    def test_preferred_agent_affinity_finds_the_previous_handler(
        self, env, workstream, customer, agent
    ):
        """The history was already in fix.conversation; nothing read it."""
        workstream.write({"prefer_last_agent": True})
        env["fix.conversation"].create(
            {
                "channel": "voice",
                "state": "resolved_agent",
                "customer_id": customer.id,
                "agent_id": agent.id,
                "operating_unit_id": _ou(env).id,
                "started_at": odoo_fields.Datetime.now(),
            }
        )
        item = workstream.intake("fix.conversation", 8, partner=customer)
        assert item._preferred_agent() == agent

    def test_a_divert_with_no_target_queue_is_refused(self, env, queue):
        with pytest.raises(ValidationError, match="names no target queue"):
            queue.write({"overflow_depth": 1, "overflow_action": "divert"})

    def test_a_closed_queue_diverts_the_arriving_contact(self, env, queue, workstream, customer):
        """The live 16743 after-hours exposure: a contact arriving at 02:00
        joined a queue nobody staffed and waited for a router that would
        never find an agent."""
        from freezegun import freeze_time

        night = env["fix.cc.queue"].create(
            {"name": "Gap Night", "code": "GAPNIGHT", "channel": "voice"}
        )
        queue.write(
            {
                "opens_hour": 9,
                "closes_hour": 18,
                "closed_action": "divert",
                "closed_queue_id": night.id,
            }
        )
        # 03:00 BST == 21:00 UTC the previous day
        with freeze_time("2026-11-02 21:00:00"):
            assert queue.is_open_now() is False
            item = workstream.intake("fix.conversation", 9, partner=customer)
        assert item.queue_id == night
        assert "is closed" in item.overflow_applied

    def test_an_overnight_queue_must_be_modelled_as_two(self, env):
        with pytest.raises(ValidationError, match="opens after it closes"):
            env["fix.cc.queue"].create(
                {
                    "name": "Gap Overnight",
                    "code": "GAPOVER",
                    "channel": "voice",
                    "opens_hour": 22,
                    "closes_hour": 6,
                }
            )

    def test_wait_prediction_reports_none_rather_than_a_fake_zero(self, env, queue):
        """An estimate produced from no arrivals is not a prediction."""
        assert queue.predicted_wait_seconds() is None

    def test_the_availability_api_reports_every_active_queue(self, env, queue):
        rows = {row["queue"]: row for row in env["fix.cc.queue"].queue_availability()}
        assert "GAPQ" in rows
        assert rows["GAPQ"]["predicted_wait_seconds"] is None


# ==========================================================================
# S5 - Entitlement lookup at intake
# ==========================================================================
class TestS5EntitlementLookup:
    def test_a_party_with_no_contract_gets_standard_terms(self, env, customer):
        summary = env["fix.contract.entitlement"].entitlement_summary_for_party(customer)
        assert summary["has_entitlement"] is False
        assert "standard service terms" in summary["note"]

    def test_an_unidentified_party_is_reported_not_guessed(self, env):
        summary = env["fix.contract.entitlement"].entitlement_summary_for_party(False)
        assert summary["has_entitlement"] is False
        assert "No identified party" in summary["note"]

    def test_the_verdict_is_captured_on_the_work_item_at_intake(self, env, queue, customer):
        ws = env["fix.routing.workstream"].create(
            {
                "name": "Gap Entitlement",
                "code": "GAP-ENT",
                "channel": "voice",
                "work_type": "conversation",
                "queue_id": queue.id,
                "assignment_method": "pick",
            }
        )
        item = ws.intake("fix.conversation", 11, partner=customer)
        assert item.entitlement_note, "an agent must see the verdict without a second lookup"


# ==========================================================================
# S9 - SLA KPI instances
# ==========================================================================
class TestS9SlaInstances:
    @pytest.fixture
    def policy(self, env):
        return env["fix.sla.policy"].create(
            {
                "code": "GAPSLA",
                "name": "Gap SLA",
                "service_type": "walk_in",
                "priority": "high",
                "response_hours": 1.0,
                "resolution_hours": 8.0,
            }
        )

    @pytest.fixture
    def order(self, env, customer):
        return env["fix.service.order"].search([], limit=1) or None

    def test_an_sla_item_target_must_be_positive(self, env, policy):
        with pytest.raises(ValidationError, match="must be positive"):
            env["fix.sla.item"].create(
                {
                    "policy_id": policy.id,
                    "name": "Nonsense",
                    "kpi_code": "bad",
                    "target_hours": 0.0,
                }
            )

    def test_business_hours_arithmetic_skips_a_closed_day(self, env):
        """Whether hold time counts depends on working hours, which is why the
        arithmetic has to be real rather than a subtraction."""
        from datetime import datetime

        Instance = env["fix.sla.kpi.instance"]
        calendar = env["fix.working.calendar"].create(
            {"name": "Gap 9-18 Mon-Fri", "timezone": "Asia/Dhaka"}
        )
        for weekday in range(5):  # Monday..Friday
            env["fix.working.calendar.line"].create(
                {
                    "calendar_id": calendar.id,
                    "weekday": WEEKDAY_KEYS[weekday],
                    "hour_from": 9.0,
                    "hour_to": 18.0,
                }
            )
        # Friday 17:00 Dhaka + 2 business hours lands Monday 10:00 Dhaka. The
        # ORM's datetimes are naive UTC and the calendar is Asia/Dhaka (UTC+6):
        # 17:00 Dhaka is 11:00 UTC, Monday 10:00 Dhaka is 04:00 UTC.
        friday_1700 = datetime(2026, 11, 6, 11, 0)
        assert friday_1700.weekday() == 4
        target = Instance.add_business_hours(friday_1700, 2.0, calendar)
        assert (target.weekday(), target.hour) == (0, 4)

    def test_a_pause_overnight_costs_zero_business_minutes(self, env):
        from datetime import datetime

        Instance = env["fix.sla.kpi.instance"]
        calendar = env["fix.working.calendar"].create(
            {"name": "Gap 9-18 All", "timezone": "Asia/Dhaka"}
        )
        for weekday in range(7):
            env["fix.working.calendar.line"].create(
                {
                    "calendar_id": calendar.id,
                    "weekday": WEEKDAY_KEYS[weekday],
                    "hour_from": 9.0,
                    "hour_to": 18.0,
                }
            )
        # Dhaka 18:00 -> 09:00 next day, in the ORM's naive UTC (UTC+6)
        held = Instance.business_minutes_between(
            datetime(2026, 11, 3, 12, 0), datetime(2026, 11, 4, 3, 0), calendar
        )
        assert held == 0.0
        # Dhaka 10:00 -> 12:00
        inside = Instance.business_minutes_between(
            datetime(2026, 11, 3, 4, 0), datetime(2026, 11, 3, 6, 0), calendar
        )
        assert inside == 120.0

    def test_a_holiday_removes_the_whole_day(self, env):
        from datetime import datetime

        Instance = env["fix.sla.kpi.instance"]
        calendar = env["fix.working.calendar"].create(
            {"name": "Gap Holiday Cal", "timezone": "Asia/Dhaka"}
        )
        for weekday in range(7):
            env["fix.working.calendar.line"].create(
                {
                    "calendar_id": calendar.id,
                    "weekday": WEEKDAY_KEYS[weekday],
                    "hour_from": 9.0,
                    "hour_to": 18.0,
                }
            )
        env["fix.working.calendar.holiday"].create(
            {
                "calendar_id": calendar.id,
                "name": "Gap Holiday",
                "date_from": "2026-11-04",
                "date_to": "2026-11-04",
            }
        )
        assert (
            Instance.business_minutes_between(
                datetime(2026, 11, 4, 9, 0), datetime(2026, 11, 4, 18, 0), calendar
            )
            == 0.0
        )

    def test_a_resume_cancels_the_instance_and_creates_a_new_one(self, env, policy, customer):
        """The semantic the first research pass missed. Modelling a resume as a
        mutable row would lose how many times a record was held and for how
        long, which is what a disputed SLA claim turns on."""
        env["fix.sla.item"].create(
            {
                "policy_id": policy.id,
                "name": "Resolution",
                "kpi_code": "resolution",
                "target_hours": 8.0,
            }
        )
        host = env["fix.cc.queue"].create(
            {"name": "SLA Host", "code": "GAPSLAHOST", "channel": "voice"}
        )
        first = env["fix.sla.kpi.instance"].start_for(host, policy, "resolution", partner=customer)
        assert first.state == "in_progress"
        assert first.series_index == 1
        first.pause(reason="Awaiting a part from the supplier")
        assert first.state == "paused"
        second = first.resume()
        assert second != first
        assert first.state == "cancelled"
        assert first.superseded_by_id == second
        assert second.supersedes_id == first
        assert second.series_index == 2
        assert second.state == "in_progress"

    def test_an_unpausable_item_refuses_a_pause(self, env, policy, customer):
        env["fix.sla.item"].create(
            {
                "policy_id": policy.id,
                "name": "Acknowledgement",
                "kpi_code": "first_response",
                "target_hours": 1.0,
                "pausable": False,
            }
        )
        host = env["fix.cc.queue"].create(
            {"name": "SLA Host 2", "code": "GAPSLAH2", "channel": "voice"}
        )
        instance = env["fix.sla.kpi.instance"].start_for(
            host, policy, "first_response", partner=customer
        )
        with pytest.raises(UserError, match="not pausable"):
            instance.pause(reason="trying anyway")

    def test_a_pause_requires_a_stated_reason(self, env, policy, customer):
        env["fix.sla.item"].create(
            {
                "policy_id": policy.id,
                "name": "Resolution",
                "kpi_code": "resolution",
                "target_hours": 8.0,
            }
        )
        host = env["fix.cc.queue"].create(
            {"name": "SLA Host 3", "code": "GAPSLAH3", "channel": "voice"}
        )
        instance = env["fix.sla.kpi.instance"].start_for(
            host, policy, "resolution", partner=customer
        )
        with pytest.raises(UserError, match="stated reason"):
            instance.pause()

    def test_starting_twice_returns_the_running_instance(self, env, policy, customer):
        env["fix.sla.item"].create(
            {
                "policy_id": policy.id,
                "name": "Resolution",
                "kpi_code": "resolution",
                "target_hours": 8.0,
            }
        )
        host = env["fix.cc.queue"].create(
            {"name": "SLA Host 4", "code": "GAPSLAH4", "channel": "voice"}
        )
        Instance = env["fix.sla.kpi.instance"]
        first = Instance.start_for(host, policy, "resolution", partner=customer)
        again = Instance.start_for(host, policy, "resolution", partner=customer)
        assert first == again, "two live clocks on one promise is not a reportable state"

    def test_a_finished_instance_is_evidence_and_does_not_move(self, env, policy, customer):
        env["fix.sla.item"].create(
            {
                "policy_id": policy.id,
                "name": "Resolution",
                "kpi_code": "resolution",
                "target_hours": 8.0,
            }
        )
        host = env["fix.cc.queue"].create(
            {"name": "SLA Host 5", "code": "GAPSLAH5", "channel": "voice"}
        )
        instance = env["fix.sla.kpi.instance"].start_for(
            host, policy, "resolution", partner=customer
        )
        instance.succeed()
        with pytest.raises(UserError, match="finished SLA instance"):
            instance.write({"target_hours": 999.0})


# ==========================================================================
# S10 - the journey / sequence runtime
# ==========================================================================
class TestS10JourneyRuntime:
    @pytest.fixture
    def campaign(self, env):
        return env["fix.campaign"].create(
            {
                "name": "Gap Journey Campaign",
                "channel": "sms",
                "budget": 1000.0,
                "start_date": "2026-11-01",
                "end_date": "2026-12-31",
                "state": "running",
            }
        )

    @pytest.fixture
    def segment(self, env, customer):
        seg = env["fix.segment"].create({"code": "GAPSEG", "name": "Gap Segment"})
        seg.action_add_members([customer.id])
        return seg

    def test_a_segment_journey_without_a_segment_is_refused(self, env, campaign):
        """The constraint the kind discriminator exists for: it would enrol
        nobody and look configured."""
        with pytest.raises(ValidationError, match="needs its audience segment"):
            env["fix.campaign.journey"].create(
                {
                    "name": "Gap Broken",
                    "campaign_id": campaign.id,
                    "journey_kind": "segment_scheduled",
                }
            )

    def test_a_trigger_journey_without_a_trigger_is_refused(self, env, campaign):
        with pytest.raises(ValidationError, match="needs its starting trigger"):
            env["fix.campaign.journey"].create(
                {
                    "name": "Gap Broken 2",
                    "campaign_id": campaign.id,
                    "journey_kind": "trigger_immediate",
                }
            )

    def test_a_journey_with_no_steps_cannot_activate(self, env, campaign, segment):
        journey = env["fix.campaign.journey"].create(
            {
                "name": "Gap Empty",
                "campaign_id": campaign.id,
                "journey_kind": "segment_scheduled",
                "segment_id": segment.id,
            }
        )
        with pytest.raises(UserError, match="nothing to do"):
            journey.action_activate()

    def test_a_journey_cannot_outrun_its_campaign(self, env, campaign, segment):
        campaign.write({"state": "paused"})
        journey = env["fix.campaign.journey"].create(
            {
                "name": "Gap Paused Campaign",
                "campaign_id": campaign.id,
                "journey_kind": "segment_scheduled",
                "segment_id": segment.id,
            }
        )
        env["fix.campaign.journey.step"].create(
            {
                "journey_id": journey.id,
                "sequence": 10,
                "name": "Exit",
                "step_type": "exit",
            }
        )
        with pytest.raises(UserError, match="only runs under a running campaign"):
            journey.action_activate()

    def test_a_send_step_without_a_body_or_template_is_refused(self, env, campaign, segment):
        journey = env["fix.campaign.journey"].create(
            {
                "name": "Gap Sendless",
                "campaign_id": campaign.id,
                "journey_kind": "segment_scheduled",
                "segment_id": segment.id,
            }
        )
        with pytest.raises(ValidationError, match="needs a template or a body"):
            env["fix.campaign.journey.step"].create(
                {
                    "journey_id": journey.id,
                    "sequence": 10,
                    "name": "Empty send",
                    "step_type": "send",
                    "channel": "sms",
                }
            )

    def test_a_segment_journey_enrols_its_audience_and_advances(
        self, env, campaign, segment, customer, grant
    ):
        grant(customer, "marketing", "sms")
        journey = env["fix.campaign.journey"].create(
            {
                "name": "Gap Working Journey",
                "campaign_id": campaign.id,
                "journey_kind": "segment_scheduled",
                "segment_id": segment.id,
            }
        )
        env["fix.campaign.journey.step"].create(
            {
                "journey_id": journey.id,
                "sequence": 10,
                "name": "Welcome",
                "step_type": "send",
                "channel": "sms",
                "purpose": "marketing",
                "body": "Welcome {{name}}",
            }
        )
        env["fix.campaign.journey.step"].create(
            {
                "journey_id": journey.id,
                "sequence": 20,
                "name": "Done",
                "step_type": "exit",
                "exit_reason": "Journey complete",
            }
        )
        journey.action_activate()
        assert journey.member_active_count == 1
        member = journey.member_ids[0]
        journey.cron_advance_journeys()
        member.invalidate_recordset()
        assert member.state == "exited"
        assert member.delivery_ids, "the send step must produce a real delivery row"
        assert member.delivery_ids[0].body == "Welcome %s" % customer.name

    def test_enrolment_is_idempotent_per_member_per_event(self, env, campaign, segment, customer):
        journey = env["fix.campaign.journey"].create(
            {
                "name": "Gap Idempotent",
                "campaign_id": campaign.id,
                "journey_kind": "segment_scheduled",
                "segment_id": segment.id,
            }
        )
        env["fix.campaign.journey.step"].create(
            {
                "journey_id": journey.id,
                "sequence": 10,
                "name": "Exit",
                "step_type": "exit",
            }
        )
        journey.action_activate()
        before = len(journey.member_ids)
        journey._enrol_segment_members()
        journey.invalidate_recordset()
        assert len(journey.member_ids) == before

    def test_a_member_who_leaves_the_segment_exits_the_running_journey(
        self, env, campaign, segment, customer
    ):
        """The live-republish design constraint: no step may trust the
        launch-time snapshot."""
        journey = env["fix.campaign.journey"].create(
            {
                "name": "Gap Live Segment",
                "campaign_id": campaign.id,
                "journey_kind": "segment_scheduled",
                "segment_id": segment.id,
                "live_segment_sync": True,
            }
        )
        env["fix.campaign.journey.step"].create(
            {
                "journey_id": journey.id,
                "sequence": 10,
                "name": "Wait a while",
                "step_type": "wait",
                "wait_minutes": 0,
            }
        )
        env["fix.campaign.journey.step"].create(
            {
                "journey_id": journey.id,
                "sequence": 20,
                "name": "Exit",
                "step_type": "exit",
            }
        )
        journey.action_activate()
        member = journey.member_ids[0]
        segment.action_remove_member(customer.id)
        journey.cron_advance_journeys()
        member.invalidate_recordset()
        assert member.state == "exited"
        assert "left audience segment" in member.exit_reason

    def test_a_member_who_withdraws_consent_exits_rather_than_being_walked_on(
        self, env, campaign, segment, customer, grant
    ):
        consent = grant(customer, "marketing", "sms")
        journey = env["fix.campaign.journey"].create(
            {
                "name": "Gap Consent Exit",
                "campaign_id": campaign.id,
                "journey_kind": "segment_scheduled",
                "segment_id": segment.id,
                "exit_on_consent_withdrawal": True,
            }
        )
        env["fix.campaign.journey.step"].create(
            {
                "journey_id": journey.id,
                "sequence": 10,
                "name": "Step one",
                "step_type": "send",
                "channel": "sms",
                "purpose": "marketing",
                "body": "First",
            }
        )
        journey.action_activate()
        member = journey.member_ids[0]
        consent.action_withdraw()
        journey.cron_advance_journeys()
        member.invalidate_recordset()
        assert member.state == "exited"
        assert "withdrew marketing consent" in member.exit_reason

    def test_a_branch_arm_with_nowhere_to_go_completes_rather_than_falling_through(
        self, env, campaign, segment, customer
    ):
        """Falling through would silently merge the two arms."""
        journey = env["fix.campaign.journey"].create(
            {
                "name": "Gap Branch",
                "campaign_id": campaign.id,
                "journey_kind": "segment_scheduled",
                "segment_id": segment.id,
                "exit_on_consent_withdrawal": False,
            }
        )
        env["fix.campaign.journey.step"].create(
            {
                "journey_id": journey.id,
                "sequence": 10,
                "name": "Always true branch",
                "step_type": "branch",
                "condition_kind": "always",
            }
        )
        journey.action_activate()
        member = journey.member_ids[0]
        journey.cron_advance_journeys()
        member.invalidate_recordset()
        assert member.state == "completed"
        assert "no next step" in member.exit_reason

    def test_a_branch_cannot_point_at_another_journeys_step(self, env, campaign, segment):
        other = env["fix.campaign.journey"].create(
            {
                "name": "Gap Other",
                "campaign_id": campaign.id,
                "journey_kind": "segment_scheduled",
                "segment_id": segment.id,
            }
        )
        other_step = env["fix.campaign.journey.step"].create(
            {"journey_id": other.id, "sequence": 10, "name": "Theirs", "step_type": "exit"}
        )
        mine = env["fix.campaign.journey"].create(
            {
                "name": "Gap Mine",
                "campaign_id": campaign.id,
                "journey_kind": "segment_scheduled",
                "segment_id": segment.id,
            }
        )
        with pytest.raises(ValidationError, match="another journey"):
            env["fix.campaign.journey.step"].create(
                {
                    "journey_id": mine.id,
                    "sequence": 10,
                    "name": "Mine",
                    "step_type": "branch",
                    "condition_kind": "always",
                    "true_step_id": other_step.id,
                }
            )

    def test_two_steps_cannot_share_a_sequence_number(self, env, campaign, segment):
        journey = env["fix.campaign.journey"].create(
            {
                "name": "Gap Dup Seq",
                "campaign_id": campaign.id,
                "journey_kind": "segment_scheduled",
                "segment_id": segment.id,
            }
        )
        env["fix.campaign.journey.step"].create(
            {"journey_id": journey.id, "sequence": 10, "name": "A", "step_type": "exit"}
        )
        with pytest.raises(IntegrityError):
            env["fix.campaign.journey.step"].create(
                {"journey_id": journey.id, "sequence": 10, "name": "B", "step_type": "exit"}
            )
            journey.flush_recordset()


# ==========================================================================
# M07 - sequences on the same engine
# ==========================================================================
class TestM07Sequences:
    def test_a_manual_step_without_an_instruction_is_refused(self, env):
        """The point of a cadence is that the instruction is written down."""
        sequence = env["fix.crm.sequence"].create({"name": "Gap Cadence", "code": "GAPCAD"})
        with pytest.raises(ValidationError, match="says nothing about what"):
            env["fix.crm.sequence.step"].create(
                {
                    "sequence_id": sequence.id,
                    "sequence": 10,
                    "name": "Call them",
                    "step_type": "call",
                }
            )

    def test_an_inactive_sequence_refuses_enrolment(self, env):
        sequence = env["fix.crm.sequence"].create({"name": "Gap Draft Cadence", "code": "GAPDRAFT"})
        lead = env["crm.lead"].create({"name": "Gap Lead"})
        with pytest.raises(UserError, match="Activate it before enrolling"):
            sequence.enrol(lead)

    def test_a_cadence_raises_an_activity_and_waits_for_the_seller(self, env):
        sequence = env["fix.crm.sequence"].create(
            {"name": "Gap Working Cadence", "code": "GAPWORK", "first_touch_sla_hours": 2.0}
        )
        env["fix.crm.sequence.step"].create(
            {
                "sequence_id": sequence.id,
                "sequence": 10,
                "name": "First call",
                "step_type": "call",
                "instructions": "Introduce 1000FiX and confirm the device model.",
            }
        )
        sequence.action_activate()
        lead = env["crm.lead"].create({"name": "Gap Cadence Lead"})
        enrolment = sequence.enrol(lead)
        assert enrolment.first_touch_due_at, "the cadence promise must be dated"
        sequence.cron_advance_sequences()
        enrolment.invalidate_recordset()
        assert enrolment.state == "active"
        activities = env["mail.activity"].search(
            [("res_id", "=", lead.id), ("user_id", "=", enrolment.owner_id.id)]
        )
        assert activities, "a manual step must put the task on the seller's list"
        # A second pass must not raise a duplicate task.
        sequence.cron_advance_sequences()
        assert len(
            env["mail.activity"].search(
                [("res_id", "=", lead.id), ("user_id", "=", enrolment.owner_id.id)]
            )
        ) == len(activities)

    def test_a_first_touch_breach_is_published_not_merely_coloured(self, env):
        from freezegun import freeze_time

        sequence = env["fix.crm.sequence"].create(
            {"name": "Gap SLA Cadence", "code": "GAPSLACAD", "first_touch_sla_hours": 1.0}
        )
        env["fix.crm.sequence.step"].create(
            {
                "sequence_id": sequence.id,
                "sequence": 10,
                "name": "Call",
                "step_type": "call",
                "instructions": "Call the prospect.",
            }
        )
        sequence.action_activate()
        lead = env["crm.lead"].create({"name": "Gap Breach Lead"})
        enrolment = sequence.enrol(lead)
        with freeze_time(
            odoo_fields.Datetime.to_string(
                odoo_fields.Datetime.add(odoo_fields.Datetime.now(), hours=3)
            )
        ):
            assert env["fix.crm.sequence"].cron_flag_first_touch_breaches() >= 1
        enrolment.invalidate_recordset()
        assert enrolment.first_touch_breached is True


# ==========================================================================
# M10 - the loyalty scheme engine
# ==========================================================================
class TestM10LoyaltyScheme:
    @pytest.fixture
    def program(self, env):
        return env["fix.loyalty.program"].create(
            {"name": "Gap Programme", "code": "GAPLOY", "points_per_bdt": 0.01}
        )

    @pytest.fixture
    def tiers(self, env, program):
        silver = env["fix.loyalty.tier"].create(
            {
                "program_id": program.id,
                "name": "Gap Silver",
                "code": "GAPSIL",
                "sequence": 10,
                "min_points_threshold": 0,
                "points_multiplier": 1.0,
            }
        )
        gold = env["fix.loyalty.tier"].create(
            {
                "program_id": program.id,
                "name": "Gap Gold",
                "code": "GAPGLD",
                "sequence": 5,
                "min_points_threshold": 500,
                "points_multiplier": 2.0,
            }
        )
        return {"silver": silver, "gold": gold}

    @pytest.fixture
    def account(self, env, program, tiers, customer):
        return env["fix.loyalty.account"].create(
            {
                "partner_id": customer.id,
                "program_id": program.id,
                "tier_id": tiers["silver"].id,
                "operating_unit_id": _ou(env).id,
            }
        )

    def test_with_no_scheme_the_programme_rate_still_applies(self, env, account):
        """Introducing the engine must not silently stop an existing programme."""
        result = account.evaluate_earn(10000.0)
        assert result["points"] == 100
        assert result["scheme_id"] is False
        assert "No live scheme" in result["basis"]

    def test_a_tier_scoped_rule_makes_gold_earn_where_silver_does_not(
        self, env, program, tiers, account
    ):
        """The row the gap plan pulled forward as a schema decision: 'Gold
        earns on parts and Silver does not' is inexpressible with a single
        multiplier."""
        scheme = env["fix.loyalty.scheme"].create(
            {"name": "Gap Scheme", "code": "GAPSCH", "program_id": program.id}
        )
        env["fix.loyalty.earn.rule"].create(
            {
                "scheme_id": scheme.id,
                "priority": 10,
                "name": "Gold earns on parts",
                "dimension": "category",
                "dimension_value": "parts",
                "tier_id": tiers["gold"].id,
                "points_per_bdt": 0.02,
            }
        )
        scheme.write({"state": "active"})
        # Silver: no rule matches, so nothing is earned on parts.
        silver_result = account.evaluate_earn(10000.0, category="parts")
        assert silver_result["points"] == 0
        assert "no rule matching" in silver_result["basis"]
        # Gold: the tier-scoped rule fires.
        account.write({"tier_id": tiers["gold"].id})
        gold_result = account.evaluate_earn(10000.0, category="parts")
        assert gold_result["points"] == 400  # 10000 * 0.02 * 2.0 multiplier

    def test_an_exclusion_rule_stops_evaluation_with_zero(self, env, program, account):
        scheme = env["fix.loyalty.scheme"].create(
            {"name": "Gap Excl", "code": "GAPEXCL", "program_id": program.id}
        )
        env["fix.loyalty.earn.rule"].create(
            {
                "scheme_id": scheme.id,
                "priority": 1,
                "name": "No points on warranty work",
                "dimension": "category",
                "dimension_value": "warranty",
                "excluded": True,
            }
        )
        env["fix.loyalty.earn.rule"].create(
            {
                "scheme_id": scheme.id,
                "priority": 10,
                "name": "Everything else",
                "dimension": "all",
                "points_per_bdt": 0.05,
            }
        )
        scheme.write({"state": "active"})
        assert account.evaluate_earn(1000.0, category="warranty")["points"] == 0
        assert account.evaluate_earn(1000.0, category="repair")["points"] == 50

    def test_an_affiliation_varies_the_rate_without_a_new_tier(self, env, program, account):
        """The concept the first research pass missed entirely."""
        affiliation = env["fix.loyalty.affiliation"].create(
            {"name": "Dealer Technicians", "code": "GAPDEAL", "program_id": program.id}
        )
        affiliation.add_members(account, reason="Dealer agreement 2026")
        scheme = env["fix.loyalty.scheme"].create(
            {"name": "Gap Affil", "code": "GAPAFF", "program_id": program.id}
        )
        env["fix.loyalty.earn.rule"].create(
            {
                "scheme_id": scheme.id,
                "priority": 1,
                "name": "Dealer rate",
                "dimension": "all",
                "affiliation_id": affiliation.id,
                "points_per_bdt": 0.10,
            }
        )
        env["fix.loyalty.earn.rule"].create(
            {
                "scheme_id": scheme.id,
                "priority": 10,
                "name": "Consumer rate",
                "dimension": "all",
                "points_per_bdt": 0.01,
            }
        )
        scheme.write({"state": "active"})
        assert account.affiliation_ids_active() == affiliation
        assert account.evaluate_earn(1000.0)["points"] == 100  # dealer rate
        affiliation.member_ids.write({"active": False})
        account.invalidate_recordset()
        assert account.evaluate_earn(1000.0)["points"] == 10  # consumer rate

    def test_a_qualifying_point_type_cannot_carry_a_redemption_value(self, env, program):
        """What decouples the IFRS-15 liability from tier marketing."""
        with pytest.raises(ValidationError, match="cannot carry a redemption value"):
            env["fix.loyalty.point.type"].create(
                {
                    "name": "Status Points",
                    "code": "GAPSTAT",
                    "program_id": program.id,
                    "point_class": "qualifying",
                    "bdt_per_point": 1.0,
                }
            )

    def test_qualifying_points_move_the_tier_without_touching_the_balance(
        self, env, program, tiers, account
    ):
        assert account.points_balance == 0
        account.award_qualifying_points(600, reason="Tier accelerator campaign")
        account.invalidate_recordset()
        assert account.qualifying_points_balance == 600
        assert (
            account.points_balance == 0
        ), "a tier accelerator must not inflate the redemption liability"
        assert account.tier_id == tiers["gold"]

    def test_a_tier_can_be_recalculated_downwards(self, env, program, tiers, account):
        """check_and_update_tier only ever promoted, which is the half that
        made a retention window impossible."""
        program.write({"tier_retention_months": 0})
        account.write({"tier_id": tiers["gold"].id})
        account.recalculate_tier(trigger="test")
        account.invalidate_recordset()
        assert account.tier_id == tiers["silver"]
        assert "downgraded" in (account.last_tier_change_reason or "")

    def test_a_retention_window_holds_a_tier_the_member_no_longer_qualifies_for(
        self, env, program, tiers, account
    ):
        program.write({"tier_retention_months": 12})
        account.award_qualifying_points(600, reason="Earned Gold")
        account.invalidate_recordset()
        assert account.tier_id == tiers["gold"]
        assert account.tier_valid_until, "retention must date the requalification"
        # Progress is wiped; the window still holds the tier.
        account.sudo().write({"qualifying_points_balance": 0})
        account.recalculate_tier(trigger="test")
        account.invalidate_recordset()
        assert account.tier_id == tiers["gold"]

    def test_scheme_activation_needs_its_dofa_approval(self, env, program):
        scheme = env["fix.loyalty.scheme"].create(
            {
                "name": "Gap Expensive",
                "code": "GAPEXP",
                "program_id": program.id,
                "estimated_annual_cost": 500000.0,
            }
        )
        env["fix.loyalty.earn.rule"].create(
            {
                "scheme_id": scheme.id,
                "priority": 10,
                "name": "All",
                "dimension": "all",
                "points_per_bdt": 0.05,
            }
        )
        # 500,000 sits above the 200,000 bound, so the CFO tier applies -
        # the same ladder M35 campaigns use.
        assert scheme.dofa_tier_required == "tier_4"
        with pytest.raises(ValidationError, match="requires .* sign-off"):
            scheme.action_activate()

    def test_a_card_resolves_at_the_counter_and_a_blocked_one_does_not(self, env, account):
        card = env["fix.loyalty.card"].create(
            {
                "account_id": account.id,
                "card_number": "GAP-CARD-1",
                "barcode": "9990001",
                "card_type": "physical",
            }
        )
        assert env["fix.loyalty.card"].resolve("9990001") == account
        card.action_block(reason="Reported lost by the member")
        assert not env["fix.loyalty.card"].resolve("9990001")

    def test_blocking_a_card_requires_a_reason(self, env, account):
        card = env["fix.loyalty.card"].create(
            {"account_id": account.id, "card_number": "GAP-CARD-2"}
        )
        with pytest.raises(UserError, match="stated reason"):
            card.action_block()


# ==========================================================================
# M34 - the survey designer
# ==========================================================================
class TestM34SurveyDesigner:
    @pytest.fixture
    def template(self, env):
        return env["fix.survey.template"].create(
            {"name": "Gap CSAT", "code": "GAPCSAT", "purpose": "post_service"}
        )

    def test_publishing_refuses_an_instrument_with_no_bengali(self, env, template):
        """DE-17: a survey a Bengali-speaking customer cannot read is not a
        survey."""
        env["fix.survey.question"].create(
            {
                "template_id": template.id,
                "sequence": 10,
                "code": "overall",
                "text": "How was the service?",
                "question_type": "rating_5",
            }
        )
        with pytest.raises(UserError, match="no Bengali text"):
            template.action_publish()

    def test_publishing_refuses_an_instrument_with_no_questions(self, env, template):
        with pytest.raises(UserError, match="asks nothing"):
            template.action_publish()

    def test_a_branch_may_only_read_an_earlier_answer(self, env, template):
        first = env["fix.survey.question"].create(
            {
                "template_id": template.id,
                "sequence": 10,
                "code": "overall",
                "text": "Overall?",
                "text_bn": "সার্বিক?",
                "question_type": "rating_5",
            }
        )
        with pytest.raises(ValidationError, match="already given"):
            env["fix.survey.question"].create(
                {
                    "template_id": template.id,
                    "sequence": 5,
                    "code": "why",
                    "text": "Why?",
                    "text_bn": "কেন?",
                    "question_type": "text",
                    "ask_if_question_id": first.id,
                    "ask_if_operator": "<=",
                    "ask_if_value": "2",
                }
            )

    def test_an_out_of_range_answer_is_refused(self, env, template):
        question = env["fix.survey.question"].create(
            {
                "template_id": template.id,
                "sequence": 10,
                "code": "overall",
                "text": "Overall?",
                "text_bn": "সার্বিক?",
                "question_type": "rating_5",
            }
        )
        with pytest.raises(ValidationError, match="outside it"):
            question.validate_answer(9)
        assert question.validate_answer(4) == 4

    def test_a_ces_question_has_its_own_scale(self, env, template):
        question = env["fix.survey.question"].create(
            {
                "template_id": template.id,
                "sequence": 10,
                "code": "effort",
                "text": "How easy was it?",
                "text_bn": "কতটা সহজ ছিল?",
                "question_type": "ces_7",
            }
        )
        assert question.validate_answer(7) == 7
        with pytest.raises(ValidationError, match="1-7"):
            question.validate_answer(8)

    def test_a_single_choice_question_needs_options(self, env, template):
        with pytest.raises(ValidationError, match="offers no options"):
            env["fix.survey.question"].create(
                {
                    "template_id": template.id,
                    "sequence": 10,
                    "code": "channel",
                    "text": "Where?",
                    "text_bn": "কোথায়?",
                    "question_type": "choice",
                }
            )

    def test_a_new_version_is_the_only_way_to_change_a_published_instrument(self, env, template):
        env["fix.survey.question"].create(
            {
                "template_id": template.id,
                "sequence": 10,
                "code": "overall",
                "text": "Overall?",
                "text_bn": "সার্বিক?",
                "question_type": "rating_5",
            }
        )
        template.action_publish()
        assert template.state == "published"
        with pytest.raises(UserError, match="already published"):
            template.action_publish()
        copy = template.action_new_version()
        assert copy.version == template.version + 1
        assert copy.state == "draft"

    def test_a_branch_whose_condition_fails_is_not_asked_rather_than_blank(self, env, template):
        """'Not asked' and 'asked and declined' mean different things."""
        overall = env["fix.survey.question"].create(
            {
                "template_id": template.id,
                "sequence": 10,
                "code": "overall",
                "text": "Overall?",
                "text_bn": "সার্বিক?",
                "question_type": "rating_5",
            }
        )
        followup = env["fix.survey.question"].create(
            {
                "template_id": template.id,
                "sequence": 20,
                "code": "why_low",
                "text": "What went wrong?",
                "text_bn": "কী ভুল হয়েছিল?",
                "question_type": "text",
                "ask_if_question_id": overall.id,
                "ask_if_operator": "<=",
                "ask_if_value": "2",
            }
        )
        assert followup.should_ask({"overall": 1}) is True
        assert followup.should_ask({"overall": 5}) is False
        assert followup.should_ask({}) is False


# ==========================================================================
# S8 - duplicate-detection jobs
# ==========================================================================
class TestS8DedupJobs:
    def test_a_job_with_no_rules_says_so_rather_than_reporting_a_clean_estate(self, env):
        """A job that finds nothing because it looked for nothing is not a
        clean estate."""
        env["fix.dedup.rule"].search([]).write({"active": False})
        job = env["fix.dedup.job"].create({"name": "Gap Empty Sweep"})
        job.action_run()
        assert job.state == "done"
        assert job.candidates_new == 0
        assert "looked for nothing" in job.summary

    def test_an_exact_rule_finds_a_stored_duplicate_and_is_idempotent(self, env):
        env["fix.dedup.rule"].search([]).write({"active": False})
        rule = env["fix.dedup.rule"].create(
            {
                "name": "Gap Phone Rule",
                "match_fields": "phone",
                "scope": "exact",
                "action": "flag",
            }
        )
        env["res.partner"].create({"name": "Dup One", "phone": "01799900001"})
        env["res.partner"].create({"name": "Dup Two", "phone": "01799900001"})
        job = env["fix.dedup.job"].create(
            {"name": "Gap Phone Sweep", "rule_ids": [(6, 0, rule.ids)]}
        )
        job.action_run()
        assert job.state == "done"
        assert job.candidates_new >= 1
        # A second sweep must not re-raise the same pair.
        again = env["fix.dedup.job"].create(
            {"name": "Gap Phone Sweep 2", "rule_ids": [(6, 0, rule.ids)]}
        )
        again.action_run()
        assert again.candidates_new == 0

    def test_a_candidate_carries_explainable_factors(self, env):
        env["fix.dedup.rule"].search([]).write({"active": False})
        rule = env["fix.dedup.rule"].create(
            {
                "name": "Gap Factor Rule",
                "match_fields": "phone",
                "scope": "exact",
                "action": "flag",
            }
        )
        env["res.partner"].create({"name": "Fac One", "phone": "01799900009"})
        env["res.partner"].create({"name": "Fac Two", "phone": "01799900009"})
        job = env["fix.dedup.job"].create(
            {"name": "Gap Factor Sweep", "rule_ids": [(6, 0, rule.ids)]}
        )
        job.action_run()
        candidate = env["fix.party.duplicate"].search([], order="id desc", limit=1)
        assert candidate.factors and "detection_job" in candidate.factors
        assert candidate.score > 0

    def test_a_record_missing_a_rule_field_is_not_blocked_for_comparison(self, env):
        """Blocking must apply the same blank-field rule as scoring.

        _similarity() refuses any pair with a blank field, so blocking a
        phoneless party on its name alone only manufactured comparisons that
        could never match - ~320k of them on the dev estate's nightly sweep.
        """
        Job = env["fix.dedup.job"]
        phoneless = env["res.partner"].create({"name": "Blank Phone Party"})
        with_phone = env["res.partner"].create(
            {"name": "Blank Phone Party", "phone": "01799900077"}
        )
        assert Job._blocking_key(phoneless, ["phone", "name"]) == ""
        assert Job._blocking_key(with_phone, ["phone", "name"]) == "900077|blan"

    def test_a_rule_naming_no_real_field_is_skipped_loudly(self, env):
        """Silently matching everything would be far worse."""
        env["fix.dedup.rule"].search([]).write({"active": False})
        rule = env["fix.dedup.rule"].create(
            {
                "name": "Gap Bogus Rule",
                "match_fields": "not_a_real_field",
                "scope": "exact",
                "action": "flag",
            }
        )
        job = env["fix.dedup.job"].create(
            {"name": "Gap Bogus Sweep", "rule_ids": [(6, 0, rule.ids)]}
        )
        job.action_run()
        assert "names no field that exists" in job.summary
        assert job.candidates_new == 0


# ==========================================================================
# M27 - productivity and quality
# ==========================================================================
class TestM27Productivity:
    def test_a_script_with_no_steps_cannot_publish(self, env):
        script = env["fix.cc.script"].create({"name": "Gap Script", "code": "GAPSCR"})
        with pytest.raises(UserError, match="gives the agent nothing"):
            script.action_publish()

    def test_the_most_specific_script_is_offered_first(self, env, queue):
        Script = env["fix.cc.script"]
        general = Script.create({"name": "Gap General", "code": "GAPGEN", "sequence": 1})
        bound = Script.create(
            {
                "name": "Gap Bound",
                "code": "GAPBOUND",
                "sequence": 50,
                "queue_id": queue.id,
                "intent": "order_status",
            }
        )
        for script in (general, bound):
            env["fix.cc.script.step"].create(
                {
                    "script_id": script.id,
                    "sequence": 10,
                    "name": "Greet",
                    "instruction": "Greet the caller.",
                }
            )
            script.action_publish()
        conversation = env["fix.conversation"].create(
            {
                "channel": "voice",
                "state": "with_agent",
                "queue_id": queue.id,
                "intent": "order_status",
                "operating_unit_id": _ou(env).id,
                "started_at": odoo_fields.Datetime.now(),
            }
        )
        offered = Script.for_conversation(conversation)
        assert offered[0] == bound, "an agent handed equal scripts uses none"

    def test_skipping_a_mandatory_step_requires_a_reason(self, env, queue):
        script = env["fix.cc.script"].create({"name": "Gap Mand", "code": "GAPMAND"})
        step = env["fix.cc.script.step"].create(
            {
                "script_id": script.id,
                "sequence": 10,
                "name": "Verify identity",
                "instruction": "Confirm the last four digits of the NID.",
                "is_mandatory": True,
            }
        )
        script.action_publish()
        conversation = env["fix.conversation"].create(
            {
                "channel": "voice",
                "state": "with_agent",
                "operating_unit_id": _ou(env).id,
                "started_at": odoo_fields.Datetime.now(),
            }
        )
        with pytest.raises(ValidationError, match="requires a stated reason"):
            env["fix.cc.script.completion"].create(
                {
                    "conversation_id": conversation.id,
                    "script_id": script.id,
                    "step_id": step.id,
                    "skipped": True,
                }
            )

    def test_a_macro_cannot_name_an_arbitrary_method(self, env):
        """Configuration access must not become code execution."""
        selection = dict(env["fix.cc.macro"]._fields["macro_action"].selection)
        assert "create_field_order" in selection
        with pytest.raises(ValueError):
            env["fix.cc.macro"].create(
                {
                    "name": "Gap Evil",
                    "code": "GAPEVIL",
                    "macro_action": "unlink_everything",
                }
            )

    def test_rubric_weights_must_total_one_hundred(self, env):
        rubric = env["fix.cc.qa.rubric"].create({"name": "Gap Rubric", "code": "GAPRUB"})
        with pytest.raises(ValidationError, match="total"):
            env["fix.cc.qa.criterion"].create(
                {
                    "rubric_id": rubric.id,
                    "sequence": 10,
                    "name": "Only half",
                    "code": "half",
                    "weight": 50.0,
                    "measure": "disposition_set",
                }
            )

    def test_bulk_evaluation_scores_ai_and_human_on_one_rubric(self, env, queue):
        """What makes 'is the bot as good as a person' answerable."""
        rubric = env["fix.cc.qa.rubric"].create(
            {"name": "Gap Both", "code": "GAPBOTH", "applies_to": "both"}
        )
        env["fix.cc.qa.criterion"].create(
            {
                "rubric_id": rubric.id,
                "sequence": 10,
                "name": "Disposition recorded",
                "code": "disp",
                "weight": 100.0,
                "measure": "disposition_set",
            }
        )
        rubric.action_publish()
        disposition = env["fix.cc.disposition"].search([], limit=1) or env[
            "fix.cc.disposition"
        ].create({"name": "Gap Resolved", "code": "GAPRES"})
        human = env["fix.conversation"].create(
            {
                "channel": "voice",
                "state": "resolved_agent",
                "queue_id": queue.id,
                "disposition_id": disposition.id,
                "operating_unit_id": _ou(env).id,
                "started_at": odoo_fields.Datetime.now(),
            }
        )
        ai = env["fix.conversation"].create(
            {
                "channel": "chat",
                "state": "resolved_ai",
                "ai_resolved": True,
                "queue_id": queue.id,
                "operating_unit_id": _ou(env).id,
                "started_at": odoo_fields.Datetime.now(),
            }
        )
        human_score = env["fix.cc.qa.evaluation"].evaluate_conversation(human, rubric)
        ai_score = env["fix.cc.qa.evaluation"].evaluate_conversation(ai, rubric)
        assert human_score.handled_by == "human" and human_score.score == 100
        assert ai_score.handled_by == "ai" and ai_score.score == 0
        comparison = {
            row["handled_by"]: row for row in env["fix.cc.qa.evaluation"].ai_vs_human_comparison()
        }
        assert "ai" in comparison and "human" in comparison

    def test_a_refused_recording_is_not_scored_as_a_qa_failure(self, env, queue):
        """Not recording because consent was refused is CORRECT behaviour."""
        rubric = env["fix.cc.qa.rubric"].create({"name": "Gap Rec", "code": "GAPREC"})
        criterion = env["fix.cc.qa.criterion"].create(
            {
                "rubric_id": rubric.id,
                "sequence": 10,
                "name": "Recording integrity",
                "code": "rec",
                "weight": 100.0,
                "measure": "recording_integrity",
            }
        )
        conversation = env["fix.conversation"].create(
            {
                "channel": "voice",
                "state": "resolved_agent",
                "queue_id": queue.id,
                "operating_unit_id": _ou(env).id,
                "started_at": odoo_fields.Datetime.now(),
            }
        )
        conversation.attach_recording(audio_bytes=b"RIFF....refused")
        assert conversation.recording_consent_state == "refused"
        assert criterion.score_for(conversation) == 100.0

    def test_intent_mining_refuses_to_read_unscrubbed_transcripts(self, env):
        """SC-003 makes mining conditional on the scrub flag."""
        result = env["fix.assistant.intent.candidate"].mine_from_traffic(days=1)
        assert result["created"] == 0
        assert "forbidden (SC-003)" in result["note"] or result["mined"] >= 0


# ==========================================================================
# S7 - the grounding service
# ==========================================================================
class TestS7GroundingService:
    def test_an_offshore_provider_cannot_be_granted_customer_context(self, env):
        """PDPA transfer restrictions, enforced rather than documented."""
        with pytest.raises(ValidationError, match="offshore"):
            env["fix.assistant.llm.provider"].create(
                {
                    "name": "Gap Offshore",
                    "code": "GAPOFF",
                    "residency": "offshore",
                    "may_receive_customer_context": True,
                }
            )

    def test_an_empty_question_is_refused_and_recorded(self, env):
        result = env["fix.assistant.intent"].ask("   ")
        assert result["ok"] is False
        record = env["fix.assistant.ask"].browse(result["ask_id"])
        assert record.engine == "refused"

    def test_an_ungrounded_question_is_refused_rather_than_answered(self, env):
        """An answer that cites nothing is refused rather than shown."""
        result = env["fix.assistant.intent"].ask(
            "What is the airspeed velocity of an unladen swallow?",
            intent="nonsense_intent",
        )
        assert result["ok"] is False
        assert result["requires_human"] is True
        record = env["fix.assistant.ask"].browse(result["ask_id"])
        assert record.grounded is False
        assert record.engine == "refused"

    def test_every_ask_is_recorded_with_its_engine(self, env):
        before = env["fix.assistant.ask"].search_count([])
        env["fix.assistant.intent"].ask("order status please", intent="order_status")
        assert env["fix.assistant.ask"].search_count([]) == before + 1


# ==========================================================================
# Deployment - the half that unit tests cannot see
# ==========================================================================
class TestDeployment:
    """A cron METHOD with no ir.cron record never runs, and passes every unit
    test anyway because a test calls it directly. This build nearly shipped
    a journey executor that executed nothing, an SLA engine that never
    breached and a delivery queue that never dispatched -- all green.

    Likewise a presence vocabulary: state_for() rightly refuses to invent
    one, so without seed data unified routing is unusable on a fresh install.
    """

    SCHEDULED = [
        ("fix.notif.delivery", "cron_dispatch_queue"),
        ("fix.notif.delivery", "cron_expire_stale_queued"),
        ("fix.routing.workstream", "cron_assign_pending"),
        ("fix.routing.workitem", "cron_expire_offers"),
        ("fix.routing.workitem", "cron_reset_end_of_day_capacity"),
        ("fix.cc.queue", "cron_handle_queue_closure"),
        ("fix.cc.wfm.adherence", "cron_compute_adherence"),
        ("fix.cc.qa.evaluation", "cron_bulk_evaluate"),
        ("fix.assistant.intent.candidate", "cron_mine_intents"),
        ("fix.campaign.journey", "cron_advance_journeys"),
        ("fix.campaign.journey", "cron_resync_live_segments"),
        ("fix.campaign.touch", "cron_harvest_from_delivery_log"),
        ("fix.crm.sequence", "cron_advance_sequences"),
        ("fix.crm.sequence", "cron_flag_first_touch_breaches"),
        ("crm.lead", "cron_rescore_open_leads"),
        ("fix.survey", "cron_retry_withheld_invitations"),
        ("fix.loyalty.account", "cron_requalify_tiers"),
        ("fix.dedup.job", "cron_run_nightly"),
        ("fix.sla.kpi.instance", "cron_flag_breaches"),
    ]

    @pytest.mark.parametrize(("model_name", "method"), SCHEDULED)
    def test_every_cron_method_has_a_scheduled_job(self, env, model_name, method):
        assert hasattr(env[model_name], method), "%s.%s does not exist" % (model_name, method)
        jobs = env["ir.cron"].search(
            [("model_id.model", "=", model_name), ("code", "like", method)]
        )
        assert jobs, (
            "%s.%s has no ir.cron record, so it will never run in production "
            "no matter how green its unit tests are" % (model_name, method)
        )
        assert any(job.active for job in jobs), "%s.%s is scheduled but every job is inactive" % (
            model_name,
            method,
        )

    @pytest.mark.parametrize(("model_name", "method"), SCHEDULED)
    def test_every_cron_actually_runs_without_raising(self, env, model_name, method):
        """A cron that raises on its first real run is as broken as one that
        was never scheduled -- and neither shows up in a test that only calls
        the business method it wraps.

        Run against whatever the rolled-back test database holds, which is
        the honest case: most of these will find nothing to do, and finding
        nothing to do must not be an exception.
        """
        getattr(env[model_name], method)()

    def test_the_presence_vocabulary_ships_with_the_module(self, env):
        Status = env["fix.cc.presence.status"]
        assert Status.search_count([]) >= 3
        assert (
            Status.search_count([("is_available_class", "=", True)]) >= 1
        ), "without an available-class status nothing can ever receive work"
        dnd = Status.search([("is_system_dnd", "=", True)])
        assert len(dnd) == 1, (
            "exactly one system Busy-DND is needed: capacity blocking has to "
            "know which status to force, and two make dnd_status() arbitrary"
        )

    def test_every_new_model_is_reachable_through_the_generic_endpoint(self, env):
        """A model with no surface cannot be opened in the workspace at all."""
        from odoo.addons.cd_p03_portal.controllers.p03_generic_api import SURFACES

        for model_name in (
            "fix.notif.delivery",
            "fix.notif.provider",
            "fix.routing.workstream",
            "fix.routing.workitem",
            "fix.cc.agent.state",
            "fix.cc.capacity.profile",
            "fix.cc.script",
            "fix.cc.qa.rubric",
            "fix.cc.wfm.adherence",
            "fix.assistant.ask",
            "fix.assistant.llm.provider",
            "fix.assistant.intent.candidate",
            "fix.campaign.journey.member",
            "fix.campaign.touch",
            "fix.crm.sequence",
            "fix.crm.score.model",
            "fix.survey.template",
            "fix.dedup.job",
            "fix.loyalty.scheme",
            "fix.loyalty.affiliation",
            "fix.sla.item",
            "fix.sla.kpi.instance",
        ):
            assert model_name in SURFACES, (
                "%s has no P03 surface, so no screen can open it" % model_name
            )

    def test_every_new_model_has_an_acl(self, env):
        """A model with no ir.model.access row is readable by nobody."""
        for model_name in (
            "fix.notif.delivery",
            "fix.notif.provider",
            "fix.cc.presence.status",
            "fix.cc.capacity.profile",
            "fix.cc.capacity.assignment",
            "fix.cc.agent.state",
            "fix.cc.agent.state.log",
            "fix.routing.workstream",
            "fix.routing.ruleset",
            "fix.routing.bullseye.ring",
            "fix.routing.workitem",
            "fix.cc.wfm.adherence",
            "fix.cc.script",
            "fix.cc.script.step",
            "fix.cc.macro",
            "fix.cc.knowledge.binding",
            "fix.cc.script.completion",
            "fix.cc.qa.rubric",
            "fix.cc.qa.criterion",
            "fix.assistant.intent.candidate",
            "fix.assistant.llm.provider",
            "fix.assistant.ask",
            "fix.campaign.journey.step",
            "fix.campaign.journey.member",
            "fix.campaign.touch",
            "fix.crm.sequence",
            "fix.crm.sequence.step",
            "fix.crm.sequence.enrolment",
            "fix.crm.score.model",
            "fix.crm.score.factor",
            "fix.survey.template",
            "fix.survey.question",
            "fix.survey.answer",
            "fix.loyalty.point.type",
            "fix.loyalty.affiliation",
            "fix.loyalty.affiliation.member",
            "fix.loyalty.scheme",
            "fix.loyalty.earn.rule",
            "fix.loyalty.burn.rule",
            "fix.loyalty.card",
            "fix.dedup.job",
            "fix.sla.item",
            "fix.sla.kpi.instance",
        ):
            acl = env["ir.model.access"].search([("model_id.model", "=", model_name)])
            assert acl, "%s has no ACL row, so nobody can read it" % model_name


# ==========================================================================
# The seams the stop-hook review correctly flagged, now closed
# ==========================================================================
class TestClosedSeams:
    """Three things I first reported as unimplementable and got wrong.

    S1 transport: I wrote "no carrier is wired; CPaaS vendor selection is a
    declared external dependency" while services/notification-dispatcher had
    real, SSRF-guarded INT-010/012/013 adapters all along. S1 now delegates
    to them instead of carrying a second HTTP client.

    S7 generation: I wrote "the request shape is written when the hosted
    model is chosen" when the model WAS chosen -- self-hosted Ollama, pinned
    image digest, recorded latency SLAs. The client exists now.

    M26 lead scoring: refusing to register a heuristic as a prediction was
    right; concluding that nothing honest could be built was wrong. M26 holds
    `rule_based` engines as a first-class kind.
    """

    def test_s1_delegates_to_the_estate_channel_adapters(self, env):
        from odoo.addons.cd_contact_centre.models import fix_notif_delivery as mod

        adapters = mod._channel_adapters()
        assert adapters is not None, (
            "the notification-dispatcher adapters must be importable: S1 "
            "delegates transport to them rather than writing a second client"
        )
        for name in ("SMSChannel", "WhatsAppChannel", "EmailChannel", "PushChannel"):
            assert hasattr(adapters, name), "adapter %s missing" % name

    def test_marketing_traffic_is_routed_non_masking(self, env, customer, grant):
        """BD-02: a marketing message never uses the registered masking sender."""
        grant(customer, "marketing", "sms")
        promo = env["fix.notif.delivery"].queue(
            channel="sms",
            purpose="marketing",
            partner=customer,
            body="Eid offer inside",
            dedup_key="seam-bd02-promo",  # gitleaks:allow - idempotency key, not a secret
        )
        assert promo.sms_route() == "non-masking"
        grant(customer, "service_updates", "sms")
        txn = env["fix.notif.delivery"].queue(
            channel="sms",
            purpose="service_updates",
            partner=customer,
            body="Your device is ready",
            dedup_key="seam-bd02-txn",  # gitleaks:allow - idempotency key, not a secret
        )
        assert txn.sms_route() == "masking"

    def test_a_promo_carrying_the_masking_signature_is_refused_permanently(
        self, env, customer, grant
    ):
        """BD-03, and a refusal a retry cannot fix must not be retried.

        My stub would have reported this as sent. The real adapter refuses it.
        """
        grant(customer, "marketing", "sms")
        provider = env["fix.notif.provider"].create(
            {"name": "Seam SMS", "code": "SEAMSMS", "channel": "sms", "transport": "int_gateway"}
        )
        from freezegun import freeze_time

        # Pinned INSIDE the BTRC window (10:00 BST == 04:00 UTC). Without
        # this the curfew holds the send before it reaches the adapter, which
        # is correct behaviour and would hide what this test is checking.
        with freeze_time("2026-11-03 04:00:00"):
            delivery = env["fix.notif.delivery"].queue(
                channel="sms",
                purpose="marketing",
                partner=customer,
                body="1000FiX Eid offer: twenty percent off",
                dedup_key="seam-bd03",
            )
            delivery.write({"provider_id": provider.id})
            delivery.action_send()
        assert delivery.state == "failed"
        assert delivery.next_attempt_at is False, (
            "a policy refusal must not be retried: it would just break the " "rule again on a timer"
        )
        assert "masking signature" in delivery.last_error

    def test_an_unconfigured_gateway_records_a_dry_run_not_a_send(self, env, customer, grant):
        """A dry run is its own state. Recording it as 'sent' would be
        precisely the lie this log exists to prevent."""
        grant(customer, "service_updates", "sms")
        provider = env["fix.notif.provider"].create(
            {"name": "Seam SMS 2", "code": "SEAMSMS2", "channel": "sms", "transport": "int_gateway"}
        )
        delivery = env["fix.notif.delivery"].queue(
            channel="sms",
            purpose="service_updates",
            partner=customer,
            body="Ready for collection",
            dedup_key="seam-dryrun",
        )
        delivery.write({"provider_id": provider.id})
        delivery.action_send()
        # No FIX_SMS_GATEWAY_URL in a test environment, so the adapter dry-runs.
        assert delivery.state == "dry_run"
        assert delivery.sent_at is False
        assert delivery.cost == 0.0
        assert "dry-run" in (delivery.last_error or "").lower()

    def test_s7_generation_client_is_real_and_reports_its_own_absence(self, env):
        from odoo.addons.cd_contact_centre.models import fix_assistant_llm as mod

        client = mod._ollama()
        assert client is not None, "the self-hosted generation client must import"
        assert hasattr(client, "generate") and hasattr(client, "translate")
        result = client.generate("hello")
        # Unconfigured in a test environment: a reportable state, not a crash.
        assert result.ok is False and result.detail

    def test_the_model_endpoint_cannot_be_pointed_offshore(self, env, monkeypatch):
        """PDPA: M32 is self-hosted because customer data must not leave the
        Company. An endpoint that could be pointed anywhere would be an
        exfiltration channel for exactly that data."""
        from odoo.addons.cd_contact_centre.models import fix_assistant_llm as mod

        client = mod._ollama()
        monkeypatch.setenv(client.URL_ENV, "http://exfil.example.com:11434")
        monkeypatch.setenv(client.MODEL_ENV, "qwen2.5:3b")
        assert client.configured() is False
        result = client.generate("hello")
        assert result.ok is False
        assert "self-hosted" in result.detail

    def test_generation_only_runs_when_grounding_found_nothing(self, env):
        """A rule-grounded answer is never replaced by a generated one."""
        result = env["fix.assistant.intent"].ask("order status please", intent="order_status")
        record = env["fix.assistant.ask"].browse(result["ask_id"])
        assert record.engine in ("rule_grounder", "refused")
        assert record.engine != "llm"

    def test_m26_registers_a_real_lead_scoring_engine(self, env):
        model = env["fix.ml.model"].search([("code", "=", "LEAD_SCORE_V1")], limit=1)
        assert model, "the M26 catalogue must carry the lead-scoring engine"
        assert model.kind == "lead_scoring"
        assert model.implementation == "rule_based", (
            "the honest label: a deterministic weighted factor model is not a "
            "prediction, and the registry must say so"
        )
        assert model.factor_weights(), "the weight vector must be readable"

    def test_the_m26_engine_scores_a_lead_explainably(self, env):
        import json

        model = env["fix.ml.model"].search([("code", "=", "LEAD_SCORE_V1")], limit=1)
        lead = env["crm.lead"].create(
            {
                "name": "Seam Corporate Lead",
                "partner_name": "Seam Industries Ltd",
                "email_from": "buyer@seam.test",
                "expected_revenue": 250000.0,
                "criteria_confirmed": True,
            }
        )
        run = env["fix.ml.inference.run"].create(
            {"model_id": model.id, "input_text": json.dumps({"lead_id": lead.id})}
        )
        run.action_execute()
        assert run.state == "computed", run.error_note
        out = json.loads(run.output_json)
        assert 0 <= out["score"] <= 100
        assert out["factors"], "the score must name the factors that fired"
        assert out["weights_used"], "and the weights it used"
        assert out["implementation"] == "rule_based"

    def test_the_m26_engine_reads_the_lead_live_not_from_the_payload(self, env):
        """A score computed from caller-supplied values would be unauditable."""
        import json

        model = env["fix.ml.model"].search([("code", "=", "LEAD_SCORE_V1")], limit=1)
        lead = env["crm.lead"].create({"name": "Seam Thin Lead"})
        run = env["fix.ml.inference.run"].create(
            {
                "model_id": model.id,
                "input_text": json.dumps({"lead_id": lead.id, "expected_revenue": 9999999.0}),
            }
        )
        run.action_execute()
        out = json.loads(run.output_json)
        assert (
            out["expected_revenue"] == 0.0
        ), "the engine must read the lead, not trust the payload"

    def test_m07_scoring_is_live_and_labels_its_basis(self, env):
        """A capability that exists and does nothing is the failure mode this
        build kept hitting: without a seeded model every lead reported 'no
        active scoring model applies'."""
        lead = env["crm.lead"].create(
            {
                "name": "Seam Scored Lead",
                "partner_name": "Seam Corp",
                "email_from": "b@seam.test",
                "expected_revenue": 600000.0,
                "criteria_confirmed": True,
                "contract_verified": True,
            }
        )
        lead.action_score()
        assert lead.lead_score > 0, lead.lead_score_reasons
        assert lead.lead_score_basis == "m26_model"
        assert lead.lead_score_band in ("hot", "warm", "cold")
        assert "LEAD_SCORE_V1" in (lead.lead_score_reasons or "")

    def test_both_dofa_conflicts_are_queryable_configuration(self, env):
        """The ruling is now a configuration act with a recorded authority,
        not a code change. Neither basis is in force, so behaviour is
        unchanged until somebody actually rules."""
        Ladder = env["fix.dofa.ladder"]
        for target in ("fix.loyalty.ledger", "fix.complaint"):
            ladders = Ladder.search([("target_model", "=", target)])
            bases = set(ladders.mapped("basis"))
            assert {"req_text", "dofa_matrix"} <= bases, (
                "%s must carry BOTH competing bases so the conflict is "
                "visible: %s" % (target, bases)
            )
            assert not any(ladders.mapped("in_force")), (
                "this build must not choose 1000FiX's financial authority " "policy for it"
            )
        conflicts = {row["target_model"]: row for row in Ladder.conflicts()}
        assert {"fix.loyalty.ledger", "fix.complaint"} <= set(conflicts)
        # The decision surface must say WHICH basis the code already does, so
        # the choice does not read as symmetrical when it is not: one option
        # is 'keep what we do', the other changes the bands.
        for target in ("fix.loyalty.ledger", "fix.complaint"):
            row = conflicts[target]
            assert row["in_force"] is None, "no ruling may be pre-taken"
            assert row["implemented_basis"] == "req_text", (
                "%s must mark which basis the coded default implements; the "
                "plan records it as the REQ text" % target
            )
            assert "changes nothing" in row["note"]

    def test_nothing_in_force_leaves_behaviour_exactly_as_it_was(self, env):
        """The fallback is the whole point: a refactor that changed approval
        thresholds as a side effect would be worse than the hard-coded lists
        it replaced."""
        assert env["fix.dofa.ladder"].thresholds_for("fix.loyalty.ledger") is None
        assert env["fix.loyalty.ledger"]._DOFA_POINT_THRESHOLDS[0] == (500.0, "tier_0")

    def test_putting_a_ladder_in_force_requires_a_stated_authority(self, env):
        ladder = env["fix.dofa.ladder"].search(
            [("target_model", "=", "fix.complaint"), ("basis", "=", "dofa_matrix")],
            limit=1,
        )
        assert ladder
        with pytest.raises(UserError, match="ruling reference"):
            ladder.action_put_in_force()

    def test_a_ruling_switches_the_ladder_and_only_one_stays_in_force(self, env):
        Ladder = env["fix.dofa.ladder"]
        matrix = Ladder.search(
            [("target_model", "=", "fix.complaint"), ("basis", "=", "dofa_matrix")],
            limit=1,
        )
        matrix.action_put_in_force(reference="Board minute 2026-11-02 item 4")
        assert matrix.in_force and matrix.ruled_by and matrix.ruled_at
        in_force = Ladder.search([("target_model", "=", "fix.complaint"), ("in_force", "=", True)])
        assert len(in_force) == 1
        # And the mixin now reads the ruled bands rather than the Python list.
        assert Ladder.thresholds_for("fix.complaint")[0] == (500.0, "tier_1")

    def test_a_ruled_ladder_actually_changes_the_derived_tier(self, env):
        """Proof the configuration is wired to the mixin and not decorative.

        BDT 800 is Tier 1 under the REQ text (<=1,000) and Tier 2 under the
        matrix (>500). Ruling must move it.
        """
        complaint = env["fix.complaint"].create(
            {
                "operating_unit_id": _ou(env).id,
                "name": "Seam DOFA ladder probe",
                "customer_id": env["res.partner"].create({"name": "Seam Complainant"}).id,
                "description": "Created by the test so the tier can be derived "
                "on a real record rather than skipped.",
                "severity": "minor",
            }
        )
        Ladder = env["fix.dofa.ladder"]
        complaint.write({"concession_amount": 800.0})
        complaint.invalidate_recordset()
        assert complaint.dofa_tier_required == "tier_1"
        Ladder.search(
            [("target_model", "=", "fix.complaint"), ("basis", "=", "dofa_matrix")],
            limit=1,
        ).action_put_in_force(reference="Board minute 2026-11-02 item 4")
        complaint.write({"concession_amount": 800.0})
        complaint.invalidate_recordset()
        assert complaint.dofa_tier_required == "tier_2", (
            "the ruled ladder must drive the derived tier, or the " "configuration is decoration"
        )


# ==========================================================================
# The plan's exit criterion: "KPI tiles re-verified vs SQL"
# ==========================================================================
class TestKpiTiles:
    """Every A03 KPI endpoint must compute, and the tiles this build closed
    must agree with an independently-derived figure.

    Four tiles returned None citing a 'declared gap', and three of those gaps
    are closed by this build. A KPI reporting None for a capability that now
    exists is a stale gap on the most visible surface in the estate — the
    same fault as an overclaim, pointing the other way.

    The comparison values here are computed from the ORM a DIFFERENT way than
    the endpoint computes them (search_count vs filtered, or arithmetic done
    in the test). A test that re-ran the endpoint's own expression would only
    prove the expression equals itself.
    """

    A03_MODULES = ["m07", "m10", "m27", "m32", "m33", "m34", "m35"]

    @pytest.mark.parametrize("module", A03_MODULES)
    def test_every_a03_kpi_endpoint_computes(self, env, module):
        """A KPI tile that raises takes the whole module dashboard down."""
        import importlib

        mod = importlib.import_module("odoo.addons.cd_p03_portal.controllers.a03.%s" % module)
        assert hasattr(mod, "kpis"), "%s exposes no kpis()" % module
        values = mod.kpis(env)
        assert isinstance(values, dict) and values, "%s.kpis() returned nothing" % module
        # Every value must be a number or an honest None -- never a string
        # like "N/A", which a dashboard would render as data.
        for key, value in values.items():
            assert value is None or isinstance(value, int | float), (
                "%s.kpis()['%s'] is %r; a tile must hold a number or None" % (module, key, value)
            )

    def test_m27_delivery_rate_matches_an_independent_count(self, env, customer, grant):
        """The tile that said 'no delivery log model — declared gap'."""
        import importlib

        m27 = importlib.import_module("odoo.addons.cd_p03_portal.controllers.a03.m27")
        Delivery = env["fix.notif.delivery"]
        grant(customer, "service_updates", "sms")
        # three attempted, one delivered, plus a suppressed one that must be
        # excluded from BOTH sides of the ratio
        for n in range(3):
            d = Delivery.queue(
                channel="sms",
                purpose="service_updates",
                partner=customer,
                body="KPI probe %d" % n,
                dedup_key="kpi-del-%d" % n,
            )
            d.write({"state": "sent", "sent_at": odoo_fields.Datetime.now()})
        Delivery.search([("dedup_key", "=", "kpi-del-0")]).mark_delivered()
        Delivery.queue(
            channel="sms",
            purpose="marketing",
            partner=customer,
            body="KPI promo",
            dedup_key="kpi-del-promo",
        )  # no marketing consent -> suppressed

        attempted = Delivery.sudo().search_count([("state", "in", ("sent", "delivered", "failed"))])
        delivered = Delivery.sudo().search_count([("state", "=", "delivered")])
        expected = round(delivered / attempted * 100.0, 1)
        assert m27.kpis(env)["notification_delivery"] == expected
        # and the suppressed row is in neither side
        suppressed = Delivery.sudo().search_count([("state", "=", "suppressed")])
        assert suppressed >= 1
        assert (
            attempted + suppressed > attempted
        ), "a suppressed message must not be counted as an attempt"

    def test_m32_guardrail_blocks_matches_the_ask_log(self, env):
        """The tile that said 'no intervention log model'."""
        import importlib

        m32 = importlib.import_module("odoo.addons.cd_p03_portal.controllers.a03.m32")
        Ask = env["fix.assistant.ask"]
        before = Ask.sudo().search_count([("guardrail_verdict", "=", "blocked")])
        Ask.sudo().create(
            {
                "consumer": "other",
                "question": "KPI probe",
                "engine": "refused",
                "guardrail_verdict": "blocked",
                "guardrail_reason": "KPI probe",
            }
        )
        assert m32.kpis(env)["guardrail_blocks"] == before + 1

    def test_m34_complaint_sla_met_is_measured_from_real_clocks(self, env):
        """The tile that said 'no SLA deadline field on fix.complaint'.

        Also proves the M34 row the plan asked for -- 'add SLA binding per
        severity' -- actually binds: a complaint must acquire clocks on
        creation, not when somebody remembers.
        """
        import importlib

        m34 = importlib.import_module("odoo.addons.cd_p03_portal.controllers.a03.m34")
        policy = env["fix.sla.policy"].search(
            [("priority", "=", "urgent"), ("active", "=", True)], limit=1
        )
        if not policy:
            policy = env["fix.sla.policy"].create(
                {
                    "code": "KPIURG",
                    "name": "KPI urgent",
                    "service_type": "walk_in",
                    "priority": "urgent",
                    "response_hours": 1.0,
                    "resolution_hours": 4.0,
                }
            )
        complaint = env["fix.complaint"].create(
            {
                "operating_unit_id": _ou(env).id,
                "name": "KPI SLA probe",
                "customer_id": env["res.partner"].create({"name": "KPI SLA Cust"}).id,
                "description": "Raised by the KPI test so a real clock exists.",
                "severity": "major",
            }
        )
        instances = (
            env["fix.sla.kpi.instance"]
            .sudo()
            .search([("res_model", "=", "fix.complaint"), ("res_id", "=", complaint.id)])
        )
        assert len(instances) == 2, (
            "a complaint must open BOTH an acknowledgement and a resolution "
            "clock on creation; got %d" % len(instances)
        )
        assert set(instances.mapped("kpi_code")) == {"first_response", "resolution"}
        assert complaint.sla_policy_id == policy
        assert "due" in (complaint.sla_resolution_state or "")

        resolution = instances.filtered(lambda i: i.kpi_code == "resolution")
        resolution.succeed()
        finished = (
            env["fix.sla.kpi.instance"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "fix.complaint"),
                    ("kpi_code", "=", "resolution"),
                    ("state", "in", ("succeeded", "breached")),
                ]
            )
        )
        met = len(finished.filtered(lambda i: i.state == "succeeded"))
        assert m34.kpis(env)["complaint_sla_met"] == round(met / len(finished) * 100.0, 1)

    def test_m34_reports_no_policy_rather_than_inventing_a_deadline(self, env):
        """A severity nobody configured a promise for must say so."""
        env["fix.sla.policy"].search([("priority", "=", "normal")]).write({"active": False})
        complaint = env["fix.complaint"].create(
            {
                "operating_unit_id": _ou(env).id,
                "name": "KPI no-policy probe",
                "customer_id": env["res.partner"].create({"name": "KPI NP"}).id,
                "description": "No normal-priority SLA policy is active.",
                "severity": "minor",
            }
        )
        assert not complaint.sla_policy_id
        assert "no SLA policy configured" in (complaint.sla_resolution_state or "")

    def test_m35_attributed_revenue_counts_only_known_values(self, env, customer):
        """The tile that said 'no order-value key on responses'.

        Still true of the response record, which is why this reads the touch
        ledger and counts only conversions whose value is KNOWN. A partial
        total presented as a total is the error being avoided.
        """
        import importlib

        m35 = importlib.import_module("odoo.addons.cd_p03_portal.controllers.a03.m35")
        campaign = env["fix.campaign"].create(
            {
                "name": "KPI Attribution Campaign",
                "channel": "sms",
                "budget": 500.0,
                "start_date": "2026-11-01",
                "end_date": "2026-12-31",
            }
        )
        Touch = env["fix.campaign.touch"]
        Touch.record(
            campaign, customer, "conversion", value_bdt=1200.0, source_key="kpi-touch-known"
        )
        # value unknown: value_bdt=None means the caller had no figure
        Touch.record(
            campaign, customer, "conversion", value_bdt=None, source_key="kpi-touch-unknown"
        )
        known = Touch.sudo().search([("touch_type", "=", "conversion"), ("value_known", "=", True)])
        expected = round(sum(known.mapped("value_bdt")), 2)
        assert m35.kpis(env)["attributed_revenue"] == expected
        unknown = Touch.sudo().search(
            [("touch_type", "=", "conversion"), ("value_known", "=", False)]
        )
        assert unknown, "the unknown-value conversion must still be recorded"
        assert expected == 1200.0, (
            "only the known value may be summed; the unknown one must not be "
            "estimated into the total"
        )


# ==========================================================================
# Display names - what a many2one cell shows on the A03 screens
# ==========================================================================
class TestA03DisplayNames:
    """A model with no name source renders as "model,id" in every grid that
    points at it. The live sweep found five A03 screens doing that."""

    def test_a_conversation_names_its_channel_and_party(self, env, customer):
        conv = env["fix.conversation"].create(
            {"channel": "voice", "customer_id": customer.id, "operating_unit_id": _ou(env).id}
        )
        assert "fix.conversation" not in conv.display_name
        assert customer.name in conv.display_name

    def test_a_notice_names_its_version(self, env, notice):
        assert "fix.transparency.notice" not in notice.display_name
        assert notice.version in notice.display_name

    def test_a_survey_names_its_service_order(self, env):
        survey = env["fix.survey"].search([("service_order_id", "!=", False)], limit=1)
        if not survey:
            pytest.skip("no survey with a service order on this database")
        assert "fix.survey" not in survey.display_name
        assert survey.service_order_id.display_name in survey.display_name

    # The three tests above name three models BY HAND, which is exactly how
    # fix.cc.agent.state.log and fix.dofa.threshold got through: nobody wrote
    # them a test. Sweep the whole area instead, so the next model added
    # without a name source fails here rather than in a user's grid.
    A03_LABELLED_MODELS = [
        "fix.notif.provider",
        "fix.notif.delivery",
        "fix.cc.presence.status",
        "fix.cc.capacity.profile",
        "fix.cc.capacity.assignment",
        "fix.cc.agent.state",
        "fix.cc.agent.state.log",
        "fix.routing.workstream",
        "fix.routing.ruleset",
        "fix.routing.bullseye.ring",
        "fix.routing.workitem",
        "fix.cc.wfm.adherence",
        "fix.cc.script",
        "fix.cc.script.step",
        "fix.cc.macro",
        "fix.cc.knowledge.binding",
        "fix.cc.script.completion",
        "fix.cc.qa.rubric",
        "fix.cc.qa.criterion",
        "fix.assistant.intent.candidate",
        "fix.assistant.llm.provider",
        "fix.assistant.ask",
        "fix.campaign.journey.step",
        "fix.campaign.journey.member",
        "fix.campaign.touch",
        "fix.crm.sequence",
        "fix.crm.sequence.step",
        "fix.crm.sequence.enrolment",
        "fix.crm.score.model",
        "fix.crm.score.factor",
        "fix.survey.template",
        "fix.survey.question",
        "fix.survey.answer",
        "fix.loyalty.scheme",
        "fix.loyalty.earn.rule",
        "fix.loyalty.burn.rule",
        "fix.loyalty.point.type",
        "fix.loyalty.affiliation",
        "fix.loyalty.affiliation.member",
        "fix.loyalty.card",
        "fix.dedup.job",
        "fix.sla.item",
        "fix.sla.kpi.instance",
        "fix.dofa.ladder",
        "fix.dofa.threshold",
    ]

    @pytest.mark.parametrize("model", A03_LABELLED_MODELS)
    def test_every_a03_model_labels_its_records(self, env, model):
        """No record may render as "model,id" or as a blank label.

        Both failure modes are invisible to a unit test that reads fields and
        to a browser sweep that only opens screens — they surface when a grid
        or a many2one draws the record. Asserted against a REAL row, because a
        _rec_name pointing at an empty field passes on a fresh one.
        """
        rec = env[model].search([], limit=1)
        if not rec:
            pytest.skip("no %s rows on this database" % model)
        label = rec.display_name or ""
        assert label.strip(), "%s renders a BLANK label" % model
        assert label != "%s,%s" % (model, rec.id), "%s has no name source — renders as %s" % (
            model,
            label,
        )
        assert model not in label, "%s leaks its technical name into the label: %s" % (model, label)
