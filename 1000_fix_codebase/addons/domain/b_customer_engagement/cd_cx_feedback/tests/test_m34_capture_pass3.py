# ruff: noqa: F811 - the P2 suite's fixtures are imported and then requested
# by name as test parameters, which ruff reads as a redefinition.
"""M34 capture audit, third pass (19 Nov 2026): the spec records no page
could capture, exercised against a real database.

Each rule is checked both ways (the wrong path is refused, the right one
works), as a non-admin user wherever the rule is about who may act:
the superuser is trusted by the field guard and would hide the gap.
"""

from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_cx_feedback.tests.test_a03_p2_cx_feedback import (  # noqa: F401
    _complaint,
    _policy,
    agent,
    closed_order,
    customer,
    env,
    make_user,
    ou,
)
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
SUPERVISOR = "cd_contact_centre.group_cc_supervisor"


@pytest.fixture
def supervisor(make_user):
    return make_user(SUPERVISOR)


@pytest.fixture
def instrument(env):
    template = env["fix.survey.template"].create(
        {
            "name": "M34 P3 CSAT",
            "name_bn": "এম৩৪ সন্তুষ্টি",
            "code": "M34P3-CSAT",
            "purpose": "post_service",
            "question_ids": [
                (
                    0,
                    0,
                    {
                        "code": "overall",
                        "text": "Overall",
                        "text_bn": "সামগ্রিক",
                        "question_type": "rating_5",
                        "sequence": 1,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "code": "effort",
                        "text": "Effort",
                        "text_bn": "প্রচেষ্টা",
                        "question_type": "ces_7",
                        "sequence": 2,
                    },
                ),
            ],
        }
    )
    template.action_publish()
    return template


@pytest.fixture
def technician(env, make_user):
    user = make_user()
    return env["hr.employee"].create({"name": "M34 P3 Technician", "user_id": user.id})


@pytest.fixture
def survey(env, closed_order, technician):
    closed_order.sudo().write({"technician_id": technician.id})
    return env["fix.survey"].consume_order_closed(
        {"event_id": "evt-m34-p3", "aggregate_id": closed_order.id}
    )


def _new_order(closed_order, technician=None):
    vals = {"state": "closed"}
    if technician:
        vals["technician_id"] = technician.id
    return closed_order.copy(vals)


# ---------------------------------------------------------------------------
# Page 2: provenance (BRU-CXM-15) and attribution (BRU-CXM-10)
# ---------------------------------------------------------------------------
class TestProvenanceAndAttribution:
    def test_a_response_without_its_channel_is_refused(self, env, agent, survey):
        with pytest.raises(ValidationError, match="BRU-CXM-15"), env.cr.savepoint():
            survey.with_user(agent).write({"rating": "4"})
        survey.invalidate_recordset()
        assert survey.state in ("pending", "sent")

    def test_a_response_records_how_when_and_who(self, env, agent, survey):
        survey.with_user(agent).write(
            {"rating": "4", "response_channel": "phone_call", "response_device": "01719000034"}
        )
        assert survey.state == "responded"
        assert survey.response_channel == "phone_call"
        assert survey.responded_at and survey.response_recorded_by_id == agent

    def test_the_channel_of_a_recorded_response_is_frozen(self, env, agent, survey):
        survey.with_user(agent).write({"rating": "4", "response_channel": "phone_call"})
        with pytest.raises(UserError, match="provenance"), env.cr.savepoint():
            survey.with_user(agent).write({"response_channel": "web_link"})

    def test_attribution_is_frozen_at_capture(self, env, survey, closed_order, technician):
        assert survey.technician_id == technician
        assert survey.branch_id == closed_order.branch_id
        other = env["hr.employee"].create({"name": "M34 P3 Other Tech"})
        closed_order.sudo().write({"technician_id": other.id})
        survey.invalidate_recordset()
        assert survey.technician_id == technician, "a reassignment moved last month's score"

    def test_record_answers_names_its_channel_too(self, env, closed_order, instrument):
        order = _new_order(closed_order)
        s = env["fix.survey"].consume_order_closed({"aggregate_id": order.id})
        s.write({"template_id": instrument.id})
        with pytest.raises(ValidationError), env.cr.savepoint():
            s.record_answers({"overall": 5})
        s.record_answers({"overall": 5}, channel="web_link", device="device-abc")
        assert s.state == "responded" and s.response_channel == "web_link"
        assert s.response_device == "device-abc"


# ---------------------------------------------------------------------------
# Page 1: triggers, sampling, delay (FR-CXM-002/003/004)
# ---------------------------------------------------------------------------
class TestSurveyTrigger:
    def _trigger(self, env, user, instrument, **vals):
        base = {
            "code": "M34P3-T",
            "name": "After repair",
            "template_id": instrument.id,
            "sampling_rate": 100,
        }
        base.update(vals)
        return env["fix.survey.trigger"].with_user(user).create(base)

    def test_only_supervisors_maintain_triggers(self, env, agent, supervisor, instrument):
        with pytest.raises(AccessError), env.cr.savepoint():
            self._trigger(env, agent, instrument)
        assert self._trigger(env, supervisor, instrument)

    def test_an_unpublished_instrument_or_a_bad_sample_is_refused(
        self, env, supervisor, instrument
    ):
        draft = instrument.copy({"code": "M34P3-DRAFT", "state": "draft"})
        with pytest.raises(ValidationError, match="not published"), env.cr.savepoint():
            self._trigger(env, supervisor, draft)
        with pytest.raises(ValidationError, match="between 1 and 100"), env.cr.savepoint():
            self._trigger(env, supervisor, instrument, sampling_rate=0)
        with pytest.raises(ValidationError, match="service type"), env.cr.savepoint():
            self._trigger(env, supervisor, instrument, service_type="not_a_type")

    def test_a_delayed_trigger_holds_then_sends(self, env, supervisor, instrument, closed_order):
        trigger = self._trigger(env, supervisor, instrument, delay_minutes=120)
        order = _new_order(closed_order)
        s = env["fix.survey"].consume_order_closed({"aggregate_id": order.id})
        assert s.trigger_id == trigger and s.template_id == instrument
        assert s.state == "pending" and s.dispatch_after and not s.dispatch_delivery_id
        assert not s.dispatch_suppressed_reason
        s.action_dispatch_invitation()
        assert s.state == "pending" and not s.dispatch_delivery_id, "sent before the delay"
        s.sudo().write({"dispatch_after": fields.Datetime.now() - timedelta(minutes=1)})
        env["fix.survey"].cron_dispatch_delayed_invitations()
        assert s.state == "sent" or s.dispatch_suppressed_reason, "the delay never released it"

    def test_an_unsampled_order_is_logged_and_cannot_be_answered(
        self, env, supervisor, instrument, closed_order
    ):
        trigger = self._trigger(env, supervisor, instrument, sampling_rate=1)
        orders = [_new_order(closed_order) for _ in range(6)]
        out = next(o for o in orders if not trigger._sampled(o))
        s = env["fix.survey"].consume_order_closed({"aggregate_id": out.id})
        assert s.state == "not_sampled" and "Not sampled" in s.dispatch_suppressed_reason
        assert not s.dispatch_delivery_id
        with pytest.raises(UserError, match="not sampled"), env.cr.savepoint():
            s.write({"rating": "5", "response_channel": "phone_call"})
        assert trigger.not_sampled_count >= 1

    def test_the_sample_is_repeatable(self, env, supervisor, instrument, closed_order):
        trigger = self._trigger(env, supervisor, instrument, sampling_rate=50)
        assert trigger._sampled(closed_order) == trigger._sampled(closed_order)

    def test_the_most_specific_trigger_wins(self, env, supervisor, instrument, closed_order):
        self._trigger(env, supervisor, instrument)
        branch = self._trigger(
            env, supervisor, instrument, code="M34P3-B", branch_id=closed_order.branch_id.id
        )
        assert env["fix.survey.trigger"]._for_order(closed_order) == branch


# ---------------------------------------------------------------------------
# Page 2: response anomalies (FR-CXM-019, BRU-CXM-11, SOD-21)
# ---------------------------------------------------------------------------
class TestResponseAnomaly:
    def _raise(self, env, user, technician, **vals):
        today = fields.Date.context_today(env.user)
        base = {
            "detection_type": "clustering",
            "scope_type": "technician",
            "technician_id": technician.id,
            "period_from": today - timedelta(days=30),
            "period_to": today,
            "evidence": "14 fives in one hour, same caller number.",
        }
        base.update(vals)
        return env["fix.cx.response.anomaly"].with_user(user).create(base)

    def test_raising_holds_the_scope_out_of_incentives(
        self, env, agent, supervisor, survey, technician
    ):
        survey.with_user(agent).write({"rating": "5", "response_channel": "phone_call"})
        anomaly = self._raise(env, supervisor, technician)
        survey.invalidate_recordset()
        assert survey.anomaly_id == anomaly and survey.incentive_excluded
        assert anomaly.held_count == 1

    def test_an_agent_cannot_raise_one(self, env, agent, technician):
        with pytest.raises(AccessError), env.cr.savepoint():
            self._raise(env, agent, technician)

    def test_the_subject_cannot_raise_investigate_or_decide(
        self, env, supervisor, technician, make_user
    ):
        technician.user_id.sudo().write({"group_ids": [(4, env.ref(SUPERVISOR).id)]})
        subject = technician.user_id
        with pytest.raises(UserError, match="SOD-21"), env.cr.savepoint():
            self._raise(env, subject, technician)
        anomaly = self._raise(env, supervisor, technician)
        with pytest.raises(UserError, match="SOD-21"), env.cr.savepoint():
            anomaly.with_user(subject).action_start_investigation()
        anomaly.with_user(supervisor).action_start_investigation()
        with pytest.raises(UserError, match="SOD-21"), env.cr.savepoint():
            anomaly.with_user(subject).action_clear(outcome="nothing")

    def test_the_state_is_not_typed(self, env, supervisor, technician):
        anomaly = self._raise(env, supervisor, technician)
        with pytest.raises(UserError), env.cr.savepoint():
            anomaly.with_user(supervisor).write({"state": "cleared"})

    def test_clear_releases_and_uphold_keeps(self, env, agent, supervisor, survey, technician):
        survey.with_user(agent).write({"rating": "5", "response_channel": "phone_call"})
        anomaly = self._raise(env, supervisor, technician)
        anomaly.with_user(supervisor).action_start_investigation()
        with pytest.raises(UserError, match="found"), env.cr.savepoint():
            anomaly.with_user(supervisor).action_clear(outcome="")
        anomaly.with_user(supervisor).action_clear(outcome="Genuine: a loyal estate.")
        survey.invalidate_recordset()
        assert anomaly.state == "cleared" and not survey.incentive_excluded

    def test_a_later_response_in_scope_joins_the_open_anomaly(
        self, env, agent, supervisor, technician, closed_order
    ):
        anomaly = self._raise(env, supervisor, technician)
        order = _new_order(closed_order, technician)
        s = env["fix.survey"].consume_order_closed({"aggregate_id": order.id})
        s.with_user(agent).write({"rating": "5", "response_channel": "sms_reply"})
        assert s.anomaly_id == anomaly and s.incentive_excluded

    def test_one_subject_per_anomaly(self, env, supervisor, technician, closed_order):
        with pytest.raises(ValidationError, match="one subject"), env.cr.savepoint():
            self._raise(env, supervisor, technician, branch_id=closed_order.branch_id.id)


# ---------------------------------------------------------------------------
# Page 3: the conversation rating (FR-CXM-015)
# ---------------------------------------------------------------------------
class TestConversationRating:
    @pytest.fixture
    def conversation(self, env, ou, customer, agent):
        conv = env["fix.conversation"].create(
            {"operating_unit_id": ou.id, "channel": "voice", "customer_id": customer.id}
        )
        conv.sudo().write({"agent_id": agent.id})
        return conv

    def _rate(self, env, user, conv, overall="2", **vals):
        base = {"conversation_id": conv.id, "overall": overall, "response_channel": "ivr"}
        base.update(vals)
        return env["fix.cx.rating"].with_user(user).create(base)

    def test_an_open_conversation_is_not_rated(self, env, agent, conversation):
        with pytest.raises(ValidationError, match="still open"), env.cr.savepoint():
            self._rate(env, agent, conversation)

    def test_a_low_rating_opens_a_loop_case_with_attribution(
        self, env, agent, conversation, customer
    ):
        conversation.sudo().write({"state": "resolved_agent"})
        rating = self._rate(env, agent, conversation, timeliness="1", behaviour="3")
        assert rating.agent_id == agent and rating.customer_id == customer
        followup = rating.followup_id
        assert followup and followup.rating_id == rating and followup.customer_id == customer
        assert followup.contact_due
        with pytest.raises(REFUSED), env.cr.savepoint():
            self._rate(env, agent, conversation, overall="5")
        with pytest.raises(UserError, match="not edited"), env.cr.savepoint():
            rating.with_user(agent).write({"overall": "5"})
        followup.with_user(agent).action_raise_complaint()
        assert followup.complaint_id.intake_channel == "contact_centre"

    def test_a_good_rating_opens_nothing(self, env, agent, conversation):
        conversation.sudo().write({"state": "resolved_agent"})
        assert not self._rate(env, agent, conversation, overall="5").followup_id


# ---------------------------------------------------------------------------
# Page 4: contact deadline and escalation (BRU-CXM-05, AUT-CXM-04)
# ---------------------------------------------------------------------------
class TestLoopEscalation:
    def test_uncontacted_escalates_to_the_branch_manager_then_the_director(
        self, env, agent, survey, closed_order, make_user
    ):
        manager = make_user()
        director = make_user()
        closed_order.branch_id.sudo().write({"manager_id": manager.id})
        env["ir.config_parameter"].sudo().set_param(
            "cd_cx_feedback.loop_escalation_user", director.login
        )
        survey.with_user(agent).write({"rating": "1", "response_channel": "phone_call"})
        followup = survey.followup_id
        assert followup.contact_due > fields.Datetime.now() + timedelta(hours=23)
        Followup = env["fix.cx.followup"]
        Followup.cron_escalate_uncontacted()
        assert followup.escalation_level == "0", "escalated before the deadline"
        followup.sudo().write({"contact_due": fields.Datetime.now() - timedelta(hours=1)})
        Followup.cron_escalate_uncontacted()
        assert followup.escalation_level == "1" and followup.escalated_to_id == manager
        Followup.cron_escalate_uncontacted()
        assert followup.escalation_level == "1", "level 2 before a further window"
        followup.sudo().write({"contact_due": fields.Datetime.now() - timedelta(hours=30)})
        Followup.cron_escalate_uncontacted()
        assert followup.escalation_level == "2" and followup.escalated_to_id == director

    def test_a_contacted_case_does_not_escalate(self, env, agent, survey):
        survey.with_user(agent).write({"rating": "1", "response_channel": "phone_call"})
        followup = survey.followup_id
        followup.with_user(agent).action_mark_contacted(note="Called, apologised.")
        followup.sudo().write({"contact_due": fields.Datetime.now() - timedelta(hours=2)})
        env["fix.cx.followup"].cron_escalate_uncontacted()
        assert followup.escalation_level == "0"


# ---------------------------------------------------------------------------
# Page 5: customer updates, intake channel, external referral
# ---------------------------------------------------------------------------
class TestComplaintUpdatesAndIntake:
    def test_an_sms_update_goes_through_the_delivery_service(self, env, agent, customer, ou):
        c = _complaint(env, agent, customer, ou)
        upd = (
            env["fix.complaint.update"]
            .with_user(agent)
            .create(
                {
                    "complaint_id": c.id,
                    "update_type": "progress",
                    "channel": "sms",
                    "content": "Part ordered; repair by Thursday.",
                }
            )
        )
        assert upd.delivery_id, "nothing was queued"
        assert upd.sent_by_id == agent and upd.sent_at
        c.invalidate_recordset()
        assert c.update_count + (1 if upd.state == "suppressed" else 0) >= 1
        with pytest.raises(UserError, match="not edited"), env.cr.savepoint():
            upd.with_user(agent).write({"content": "Changed my mind"})

    def test_a_call_is_recorded_as_made(self, env, agent, customer, ou):
        c = _complaint(env, agent, customer, ou)
        upd = (
            env["fix.complaint.update"]
            .with_user(agent)
            .create(
                {"complaint_id": c.id, "channel": "phone_call", "content": "Explained the delay."}
            )
        )
        assert upd.state == "sent" and not upd.delivery_id
        c.invalidate_recordset()
        assert c.last_update_at == upd.sent_at

    def test_a_closed_complaint_takes_only_a_closure_notice(self, env, agent, customer, ou):
        c = _complaint(env, agent, customer, ou)
        c.sudo().write({"state": "closed"})
        Update = env["fix.complaint.update"].with_user(agent)
        with pytest.raises(ValidationError, match="closure"), env.cr.savepoint():
            Update.create({"complaint_id": c.id, "channel": "phone_call", "content": "x"})
        assert Update.create(
            {
                "complaint_id": c.id,
                "channel": "phone_call",
                "update_type": "closure",
                "content": "Closed as agreed.",
            }
        )

    def test_staff_keyed_intake_records_its_channel(self, env, agent, customer, ou):
        c = _complaint(env, agent, customer, ou, received_via="counter")
        assert c.intake_channel == "counter"
        with pytest.raises(UserError, match="intake"), env.cr.savepoint():
            c.with_user(agent).write({"received_via": "email"})
        with pytest.raises(UserError), env.cr.savepoint():
            c.with_user(agent).write({"intake_channel": "portal"})

    def test_a_regulator_referral_names_the_body(self, env, agent, customer, ou):
        with pytest.raises(ValidationError, match="FR-CXM-038"), env.cr.savepoint():
            _complaint(env, agent, customer, ou, received_via="regulator")
        c = _complaint(
            env,
            agent,
            customer,
            ou,
            received_via="regulator",
            external_body="DNCRP",
            external_reference="DNCRP/2026/118",
        )
        assert c.intake_channel == "regulator"


# ---------------------------------------------------------------------------
# Page 6: SLA by customer tier (FR-CXM-031)
# ---------------------------------------------------------------------------
class TestTieredSla:
    def test_the_customers_tier_binding_wins(self, env, agent, customer, ou):
        program = env["fix.loyalty.program"].create(
            {
                "name": "M34 P3 Club",
                "code": "M34P3CLUB",
                "points_per_bdt": 0.01,
                "bdt_per_point": 0.5,
            }
        )
        Tier = env["fix.loyalty.tier"]
        gold = Tier.create(
            {"program_id": program.id, "name": "Gold", "code": "M34P3G", "sequence": 1}
        )
        silver = Tier.create(
            {"program_id": program.id, "name": "Silver", "code": "M34P3S", "sequence": 2}
        )
        env["fix.loyalty.account"].create(
            {"partner_id": customer.id, "program_id": program.id, "tier_id": gold.id}
        )
        Rule = env["fix.complaint.sla.rule"]
        everyone = Rule.create({"severity": "minor", "policy_id": _policy(env, "M34P3-ALL").id})
        Rule.create(
            {
                "severity": "minor",
                "policy_id": _policy(env, "M34P3-SILV").id,
                "loyalty_tier_id": silver.id,
            }
        )
        golden = Rule.create(
            {
                "severity": "minor",
                "policy_id": _policy(env, "M34P3-GOLD", resolution=8.0).id,
                "loyalty_tier_id": gold.id,
            }
        )
        member = _complaint(env, agent, customer, ou)
        assert Rule._match(member) == golden
        stranger = env["res.partner"].create({"name": "M34 P3 Walk-in"})
        walk_in = _complaint(env, agent, stranger, ou)
        assert Rule._match(walk_in) == everyone, "another tier's binding applied"


# ---------------------------------------------------------------------------
# Page 8: journeys (FR-CXM-039) and themes (FR-CXM-041)
# ---------------------------------------------------------------------------
class TestJourneysAndThemes:
    def test_a_stage_effort_question_must_exist_on_its_instrument(
        self, env, supervisor, instrument
    ):
        Journey = env["fix.journey.definition"].with_user(supervisor)
        with pytest.raises(ValidationError, match="no question"), env.cr.savepoint():
            Journey.create(
                {
                    "code": "J-REPAIR",
                    "name": "Repair",
                    "name_bn": "মেরামত",
                    "stage_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Collect",
                                "template_id": instrument.id,
                                "effort_question_code": "nope",
                            },
                        )
                    ],
                }
            )
        journey = Journey.create(
            {
                "code": "J-REPAIR",
                "name": "Repair",
                "name_bn": "মেরামত",
                "stage_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Collect",
                            "template_id": instrument.id,
                            "effort_question_code": "effort",
                        },
                    ),
                    (0, 0, {"name": "Diagnose"}),
                ],
            }
        )
        assert journey.stage_count == 2

    def test_an_agent_cannot_define_a_journey(self, env, agent):
        with pytest.raises(AccessError), env.cr.savepoint():
            env["fix.journey.definition"].with_user(agent).create(
                {"code": "J-X", "name": "X", "name_bn": "এক্স"}
            )

    def test_a_theme_counts_what_customers_wrote(
        self, env, agent, supervisor, survey, customer, ou
    ):
        survey.with_user(agent).write(
            {"rating": "2", "response_channel": "phone_call", "comment": "Waited 3 weeks for parts"}
        )
        silent_order = survey.service_order_id.copy({"state": "closed"})
        silent = env["fix.survey"].consume_order_closed({"aggregate_id": silent_order.id})
        silent.with_user(agent).write({"rating": "2", "response_channel": "phone_call"})
        Theme = env["fix.voc.theme"].with_user(supervisor)
        base = {"period": "2026-11", "theme": "Parts wait", "theme_bn": "যন্ত্রাংশ অপেক্ষা"}
        with pytest.raises(ValidationError, match="comment"), env.cr.savepoint():
            Theme.create(dict(base, survey_ids=[(6, 0, [silent.id])]))
        with pytest.raises(ValidationError, match="YYYY-MM"), env.cr.savepoint():
            Theme.create(dict(base, period="Nov 2026"))
        complaint = _complaint(env, agent, customer, ou)
        theme = Theme.create(
            dict(base, survey_ids=[(6, 0, [survey.id])], complaint_ids=[(6, 0, [complaint.id])])
        )
        assert theme.frequency == 2


def test_held_responses_stay_out_of_the_m57_csat(env, agent, survey, technician, closed_order):
    """AUT-CXM-13: technician CSAT goes to M57 without flagged responses."""
    if "fix.performance.scorecard" not in env:
        pytest.skip("M57 is not installed on this database")
    from unittest import mock

    second = env["fix.survey"].consume_order_closed(
        {"aggregate_id": _new_order(closed_order, technician).id}
    )
    survey.with_user(agent).write({"rating": "5", "response_channel": "phone_call"})
    second.with_user(agent).write({"rating": "1", "response_channel": "phone_call"})
    orders = survey.service_order_id | second.service_order_id
    card = env["fix.performance.scorecard"].new({"employee_id": technician.id, "period": "2026-11"})
    Card = type(env["fix.performance.scorecard"])
    with mock.patch.object(Card, "_fix_counted_orders", lambda self: orders):
        before = card._fix_service_order_facts()[0]["csat"]
        survey.sudo().write({"incentive_excluded": True})
        values, _n, basis = card._fix_service_order_facts()
    assert before == 0.5 and values["csat"] == 0.0, (before, values["csat"])
    assert "held by an anomaly review" in basis
