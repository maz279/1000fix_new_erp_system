"""A03 P2 — M34 complaint lifecycle, SLA, intake, concession and surveys.

Every control is exercised as a NON-ADMIN user (the superuser is trusted by
the field guard and hid every gap the audit found), and each is checked both
ways: the bypass is refused and the legitimate path works. Findings covered:
M34-1..M34-10 (working/A03_evidence/module_findings/M34_and_approval_plumbing.md).
"""

import importlib
import re
from datetime import timedelta
from pathlib import Path

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

REFUSED = (UserError, ValidationError, AccessError)
TIER_GROUP = {
    "tier_1": "cd_entity_config.group_dofa_tier_1",
    "tier_2": "cd_entity_config.group_dofa_tier_2",
    "tier_3": "cd_entity_config.group_dofa_tier_3",
    "tier_4": "cd_entity_config.group_dofa_tier_4",
}
RCA = (
    "Why1 the board shorted; Why2 flux residue; Why3 cleaning skipped; "
    "Why4 no bench checklist; Why5 SOP never updated."
)


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def make_user(env):
    counter = {"n": 0}

    def _make(*xmlids, portal=False):
        counter["n"] += 1
        base = "base.group_portal" if portal else "base.group_user"
        groups = [env.ref(base).id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "M34 P2 User %d" % counter["n"],
                    "login": "m34.p2.%d@a03.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def ou(env):
    return env["operating.unit"].search([], limit=1)


@pytest.fixture
def customer(env):
    return env["res.partner"].create({"name": "M34 P2 Customer", "phone": "01719000034"})


@pytest.fixture
def agent(make_user):
    return make_user()


@pytest.fixture
def closed_order(env, ou, customer):
    company = env["res.company"].create({"name": "M34 P2 Co"})
    entity = env["fix.entity"].create(
        {"code": "M34P2", "legal_name": "M34 P2 Entity", "company_id": company.id}
    )
    branch = env["fix.branch"].create(
        {"name": "M34 Gulshan", "code": "M34G", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "M34Brand", "code": "M34B"})
    model = env["fix.device.model"].create({"name": "M34 Phone", "brand_id": brand.id})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-M34-P2"}
    )
    return env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "No display",
            "state": "closed",
        }
    )


def _complaint(env, user, customer, ou, **vals):
    base = {
        "name": "M34-P2 complaint",
        "customer_id": customer.id,
        "operating_unit_id": ou.id,
        "description": "Device came back with the same fault.",
        "severity": "minor",
    }
    base.update(vals)
    return env["fix.complaint"].with_user(user).create(base)


def _policy(env, code, priority="normal", response=2.0, resolution=24.0):
    return env["fix.sla.policy"].create(
        {
            "code": code,
            "name": "M34 %s" % code,
            "service_type": "walk_in",
            "priority": priority,
            "response_hours": response,
            "resolution_hours": resolution,
        }
    )


def _clocks(env, complaint, kpi=None, live=None):
    domain = [("res_model", "=", "fix.complaint"), ("res_id", "=", complaint.id)]
    if kpi:
        domain.append(("kpi_code", "=", kpi))
    if live is True:
        domain.append(("state", "in", ("in_progress", "paused")))
    return env["fix.sla.kpi.instance"].sudo().search(domain)


def _events(env, event_type, res_id):
    return env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", res_id)]
    )


def _relay(env, event_type):
    """Make our consumer old enough and run the relay cron."""
    env["fix.event.consumer"].search([("event_type", "=", event_type)]).write(
        {"active_from": fields.Datetime.now() - timedelta(days=1)}
    )
    env["fix.event.outbox"].cron_relay()


def _to_accepted(c, response="We repaired the device again at no charge."):
    c.action_assess()
    c.action_investigate()
    c.action_respond(response)
    c.action_customer_accept()


# ==========================================================================
# 1. The ISO 10002 cl. 7 lifecycle as guarded transitions (M34-1/2/3)
# ==========================================================================
class TestLifecycle:
    def test_the_full_path_runs_as_plain_users(self, env, make_user, agent, customer, ou):
        raiser, verifier = make_user(), make_user()
        c = _complaint(env, raiser, customer, ou).with_user(agent)
        assert c.state == "new" and c.acknowledged_at
        c.action_assess("major: device returned damaged")
        assert (c.state, c.severity, c.owner_id) == ("assessed", "major", agent)
        c.action_investigate()
        c.root_cause_5why = RCA
        assert c.root_cause_author_id == agent
        c.action_record_root_cause()
        c.with_user(verifier).action_verify_root_cause()
        c.capa_stub_ref = "CAPA/2026/M34"
        c.action_open_capa()
        c.action_request_verification()
        assert c.state == "verification"
        c.action_respond("Replaced the screen; bench SOP updated.")
        assert (c.state, c.customer_decision) == ("responded", "pending")
        c.action_customer_accept("Happy with the fix")
        c.action_close("Screen replaced and confirmed with the customer.")
        assert c.state == "closed" and c.closed_at
        assert _events(env, "complaint.assessed", c.id)
        assert _events(env, "complaint.responded", c.id)

    def test_lifecycle_jumps_are_refused(self, env, agent, customer, ou):
        c = _complaint(env, agent, customer, ou)
        with pytest.raises(UserError, match="Assess"):
            c.action_investigate()
        with pytest.raises(UserError, match="investigated"):
            c.action_respond("anything")
        with pytest.raises(UserError, match="customer accepts"):
            c.action_close("closing early")
        with pytest.raises(UserError, match="awaiting the customer"):
            c.action_customer_accept()
        with pytest.raises(UserError, match="changes only through its workflow"):
            c.write({"state": "accepted"})
        c.action_assess()
        c.action_investigate()
        with pytest.raises(UserError, match="customer accepts"):
            c.action_close("still investigating")
        assert c.state == "investigating"

    def test_the_customer_can_reject_the_response(self, env, agent, customer, ou):
        c = _complaint(env, agent, customer, ou)
        c.action_assess()
        c.action_investigate()
        c.action_respond("We offer a re-repair.")
        with pytest.raises(UserError, match="why"):
            c.action_customer_reject("")
        c.action_customer_reject("Wants a replacement device")
        assert (c.state, c.customer_decision, c.customer_rejection_count) == (
            "investigating",
            "rejected",
            1,
        )
        c.action_respond("Replacement device offered.")
        c.action_customer_accept()
        c.action_close("Device replaced.")
        assert c.state == "closed"

    def test_decline_needs_a_reason_and_only_before_a_response(self, env, agent, customer, ou):
        c = _complaint(env, agent, customer, ou)
        with pytest.raises(UserError, match="not upheld"):
            c.action_decline("  ")
        c.action_decline("Duplicate of an earlier complaint.")
        assert (c.state, c.resolution) == ("rejected", "Duplicate of an earlier complaint.")
        answered = _complaint(env, agent, customer, ou)
        answered.action_assess()
        answered.action_investigate()
        answered.action_respond("Re-repair offered.")
        with pytest.raises(UserError, match="not yet answered"):
            answered.action_decline("too late")


class TestOwnership:
    def test_assignment_notifies_the_new_owner(self, env, make_user, agent, customer, ou):
        owner = make_user()
        c = _complaint(env, agent, customer, ou)
        c.action_assign(owner.login)
        assert c.owner_id == owner and c.assigned_at
        activity = env["mail.activity"].search(
            [("res_model", "=", "fix.complaint"), ("res_id", "=", c.id), ("user_id", "=", owner.id)]
        )
        assert activity, "the new owner was not notified"
        assert _events(env, "complaint.assigned", c.id)

    def test_the_owner_cannot_be_typed_in(self, env, make_user, agent, customer, ou):
        c = _complaint(env, agent, customer, ou)
        with pytest.raises(UserError, match="changes only through its workflow"):
            c.write({"owner_id": make_user().id})
        with pytest.raises(UserError, match="No active internal user"):
            c.action_assign("nobody.at.all@a03.test")
        portal = make_user(portal=True)
        with pytest.raises(UserError, match="No active internal user"):
            c.action_assign(portal.login)
        c.action_take_ownership()
        assert c.owner_id == agent

    def test_severity_is_frozen_after_assessment(self, env, agent, customer, ou):
        c = _complaint(env, agent, customer, ou, severity="critical")
        c.action_assess()
        with pytest.raises(UserError, match="cannot be changed"):
            c.write({"severity": "minor"})
        with pytest.raises(UserError, match="needs a stated reason"):
            c.action_reassess("minor")
        c.action_reassess("minor: customer confirmed only a cosmetic scratch")
        assert c.severity == "minor"
        assert "cosmetic scratch" in c.message_ids[0].body


class TestFiveWhyGate:
    def test_a_major_complaint_waits_for_a_verified_5why(self, env, make_user, agent, customer, ou):
        verifier = make_user()
        c = _complaint(env, agent, customer, ou, severity="major")
        c.action_assess()
        c.action_investigate()
        with pytest.raises(ValidationError, match="5-Why"):
            c.action_respond("Fixed.")
        c.root_cause_5why = RCA
        with pytest.raises(ValidationError, match="not verified"):
            c.action_respond("Fixed.")
        with pytest.raises(UserError, match="changes only through its workflow"):
            c.write({"five_why_verified": True})
        with pytest.raises(UserError, match="Segregation of duties"):
            c.action_verify_root_cause()
        c.with_user(verifier).action_verify_root_cause()
        assert c.five_why_verified and c.five_why_verified_by_id == verifier
        # editing the verified analysis withdraws the verification
        c.root_cause_5why = RCA + " Why6 added later."
        assert not c.five_why_verified
        c.with_user(verifier).action_verify_root_cause()
        c.action_respond("Fixed and the bench SOP updated.")
        assert c.state == "responded"


class TestReopen:
    def test_reopen_rules(self, env, agent, customer, ou):
        c = _complaint(env, agent, customer, ou)
        _to_accepted(c)
        c.action_close("Repaired.")
        assert c.post_closure_survey_sent_at
        with pytest.raises(UserError, match="why"):
            c.action_reopen("")
        c.action_reopen("Fault came back after two days")
        assert (c.state, c.reopen_count) == ("investigating", 1)
        assert not c.post_closure_survey_sent_at and not c.closed_at
        assert c.customer_decision is False
        with pytest.raises(UserError, match="closed or declined"):
            c.action_reopen("again")
        c.action_respond("Second repair done.")
        c.action_customer_accept()
        c.action_close("Second repair confirmed.")
        # the re-armed survey goes out again after the second closure
        assert len(_events(env, "complaint.post_closure_survey_dispatched", c.id)) == 2

    def test_reopen_outside_the_window_is_refused(self, env, agent, customer, ou):
        c = _complaint(env, agent, customer, ou)
        _to_accepted(c)
        c.action_close("Repaired.")
        c.sudo().write({"closed_at": fields.Datetime.now() - timedelta(days=45)})
        with pytest.raises(UserError, match="raise a new complaint"):
            c.action_reopen("Too late")


# ==========================================================================
# 2. SLA clocks (M34-5)
# ==========================================================================
class TestSlaClocks:
    def test_clocks_stop_on_close(self, env, agent, customer, ou):
        rule_policy = _policy(env, "M34STOP")
        env["fix.complaint.sla.rule"].create({"severity": "minor", "policy_id": rule_policy.id})
        c = _complaint(env, agent, customer, ou)
        assert len(_clocks(env, c, live=True)) == 2
        c.action_assess()
        assert _clocks(env, c, "first_response").state == "succeeded"
        c.action_investigate()
        c.action_respond("Re-repaired.")
        c.action_customer_accept()
        c.action_close("Re-repaired.")
        assert not _clocks(env, c, live=True), "a closed complaint's clocks kept running"
        assert _clocks(env, c, "resolution").state == "succeeded"

    def test_a_severity_change_rebinds_the_policy(self, env, agent, customer, ou):
        slow = _policy(env, "M34SLOW", response=8.0, resolution=72.0)
        fast = _policy(env, "M34FAST", priority="emergency", response=1.0, resolution=4.0)
        Rule = env["fix.complaint.sla.rule"]
        Rule.create({"severity": "minor", "policy_id": slow.id})
        Rule.create({"severity": "critical", "policy_id": fast.id})
        c = _complaint(env, agent, customer, ou)
        assert c.sla_policy_id == slow
        origin = _clocks(env, c, "resolution", live=True).started_at
        c.action_assess()
        c.action_reassess("critical")
        assert c.sla_policy_id == fast
        live = _clocks(env, c, "resolution", live=True)
        assert live.policy_id == fast and live.target_hours == 4.0
        assert live.started_at == origin, "the new deadline runs from intake"
        old = _clocks(env, c, "resolution").filtered(lambda i: i.policy_id == slow)
        assert old.state == "cancelled"

    def test_the_policy_follows_branch_then_operating_unit(
        self, env, agent, customer, ou, closed_order
    ):
        estate, unit, branch = (
            _policy(env, "M34EST"),
            _policy(env, "M34OU"),
            _policy(env, "M34BR"),
        )
        Rule = env["fix.complaint.sla.rule"]
        Rule.create({"severity": "minor", "policy_id": estate.id})
        Rule.create({"severity": "minor", "operating_unit_id": ou.id, "policy_id": unit.id})
        assert _complaint(env, agent, customer, ou).sla_policy_id == unit
        Rule.create(
            {"severity": "minor", "branch_id": closed_order.branch_id.id, "policy_id": branch.id}
        )
        at_branch = _complaint(env, agent, customer, ou, service_order_id=closed_order.id)
        assert at_branch.sla_policy_id == branch

    def test_backfill_opens_missing_clocks_once(self, env, agent, customer, ou):
        env["fix.sla.policy"].search([]).write({"active": False})
        c = _complaint(env, agent, customer, ou)
        assert not _clocks(env, c)
        policy = _policy(env, "M34BACK")
        env["fix.complaint.sla.rule"].create({"severity": "minor", "policy_id": policy.id})
        result = env["fix.complaint"].cron_backfill_sla_clocks()
        assert result["clocks_started"] >= 2
        assert set(_clocks(env, c).mapped("kpi_code")) == {"first_response", "resolution"}
        assert _clocks(env, c, "resolution").started_at == c.create_date
        assert env["fix.complaint"].cron_backfill_sla_clocks()["clocks_started"] == 0
        assert env.ref("cd_cx_feedback.ir_cron_complaint_backfill_sla").active


# ==========================================================================
# 3. Intake (M34-8)
# ==========================================================================
class TestIntake:
    def test_a_conversation_raises_one_complaint(self, env, agent, customer, ou):
        conv = env["fix.conversation"].create(
            {"operating_unit_id": ou.id, "channel": "voice", "customer_id": customer.id}
        )
        env["fix.conversation.turn"].create(
            {
                "conversation_id": conv.id,
                "speaker": "customer",
                "text": "My phone still won't charge.",
            }
        )
        conv = conv.with_user(agent)
        result = conv.action_create_complaint()
        complaint = conv.complaint_id
        assert result["res_id"] == complaint.id
        assert (complaint.intake_channel, complaint.conversation_id) == ("contact_centre", conv)
        assert complaint.customer_id == customer
        assert "won't charge" in complaint.description
        conv.action_create_complaint()
        assert env["fix.complaint"].search_count([("conversation_id", "=", conv.id)]) == 1
        with pytest.raises(UserError, match="changes only through its workflow"):
            conv.write({"complaint_id": False})

    def test_a_conversation_without_a_customer_is_refused(self, env, agent, ou):
        conv = env["fix.conversation"].create({"operating_unit_id": ou.id, "channel": "voice"})
        with pytest.raises(UserError, match="Identify the customer"):
            conv.with_user(agent).action_create_complaint()

    def test_the_portal_files_only_for_the_signed_in_customer(
        self, env, make_user, agent, closed_order
    ):
        portal = make_user(portal=True)
        other = env["res.partner"].create({"name": "Someone Else"})
        Complaint = env["fix.complaint"].with_user(portal)
        summary = Complaint.portal_submit_complaint(
            subject="Screen flickers",
            description="The screen flickers since the repair.",
            request_ref="req-1",
            partner_id=other.id,  # ignored for a portal user
        )
        c = env["fix.complaint"].browse(summary["id"])
        assert (c.customer_id, c.intake_channel) == (portal.partner_id, "portal")
        again = Complaint.portal_submit_complaint(
            subject="Screen flickers", description="retry", request_ref="req-1"
        )
        assert again["id"] == c.id, "a retried submission must not create a second complaint"
        with pytest.raises(UserError, match="not one of yours"):
            Complaint.portal_submit_complaint(
                subject="x", description="y", service_order_id=closed_order.id
            )
        with pytest.raises(UserError, match="subject"):
            Complaint.portal_submit_complaint(subject="", description="")
        assert [r["id"] for r in Complaint.portal_list_complaints()] == [c.id]
        # the customer decides on the response from the portal
        work = c.with_user(agent)
        work.action_assess()
        work.action_investigate()
        work.action_respond("We will replace the screen.")
        assert Complaint.portal_complaint_decision(complaint_id=c.id, accept=True)["state"] == (
            "accepted"
        )
        stranger = make_user(portal=True)
        with pytest.raises(UserError, match="not one of yours"):
            env["fix.complaint"].with_user(stranger).portal_complaint_decision(
                complaint_id=c.id, accept=False, note="no"
            )

    def test_a_detractor_follow_up_raises_or_links_a_complaint(self, env, agent, closed_order):
        survey = env["fix.survey"].consume_order_closed(
            {"event_id": "evt-m34-p2-det", "aggregate_id": closed_order.id}
        )
        survey.write({"rating": "2", "comment": "Rude technician"})
        followup = survey.followup_id.with_user(agent)
        followup.action_raise_complaint()
        complaint = followup.complaint_id
        assert complaint.intake_channel == "survey" and followup.reason == "complaint_linked"
        assert complaint.service_order_id == closed_order
        followup.action_raise_complaint()
        assert (
            env["fix.complaint"].search_count([("intake_ref", "=", "followup:%d" % followup.id)])
            == 1
        )


# ==========================================================================
# 4. The approved concession produces its money document (M34-9)
# ==========================================================================
def _approved_concession(env, make_user, raiser, customer, ou, amount, ctype, **vals):
    c = _complaint(
        env,
        raiser,
        customer,
        ou,
        concession_amount=amount,
        concession_type=ctype,
        dofa_justification="Repeat failure on the same repair.",
        **vals,
    )
    approver = make_user(TIER_GROUP[c._dofa_current_tier()])
    approve_via_inbox(c, approver, raiser)
    assert c.concession_approved
    assert _events(env, "complaint.concession_approved", c.id)
    return c


class TestConcessionDocument:
    def test_a_concession_needs_a_type_and_an_open_complaint(self, env, agent, customer, ou):
        c = _complaint(env, agent, customer, ou, concession_amount=800.0)
        with pytest.raises(UserError, match="concession type"):
            c.action_request_approval()

    def test_an_unapproved_concession_cannot_be_offered(self, env, agent, customer, ou):
        c = _complaint(
            env, agent, customer, ou, concession_amount=800.0, concession_type="discount"
        )
        c.action_assess()
        c.action_investigate()
        with pytest.raises(ValidationError, match="DOFA approval"):
            c.action_respond("Voucher offered")

    def test_a_discount_becomes_one_voucher(self, env, make_user, agent, customer, ou):
        raiser = make_user()
        c = _approved_concession(env, make_user, raiser, customer, ou, 800.0, "discount")
        c = c.with_user(agent)
        _to_accepted(c, "BDT 800 voucher for your next repair.")
        c.action_close("Voucher issued.")
        voucher = env["fix.loyalty.voucher"].search([("complaint_id", "=", c.id)])
        assert len(voucher) == 1
        assert (voucher.partner_id, voucher.discount_value, voucher.state) == (
            customer,
            800.0,
            "active",
        )
        c.sudo()._settle_concession()
        assert env["fix.loyalty.voucher"].search_count([("complaint_id", "=", c.id)]) == 1
        assert c.concession_settled_amount == 800.0

    def test_a_refund_becomes_a_credit_note_on_the_order_invoice(
        self, env, make_user, agent, customer, ou, closed_order
    ):
        invoice = env["fix.ar.invoice"].create(
            {
                "operating_unit_id": ou.id,
                "customer_id": customer.id,
                "source_model": "fix.service.order",
                "source_id": closed_order.id,
                "state": "issued",
                "line_ids": [
                    (0, 0, {"description": "Repair", "taxable_amount": 5000.0, "vat_amount": 750.0})
                ],
            }
        )
        raiser = make_user()
        c = _approved_concession(
            env, make_user, raiser, customer, ou, 2000.0, "refund", service_order_id=closed_order.id
        )
        c = c.with_user(agent)
        _to_accepted(c, "BDT 2,000 refund.")
        c.action_close("Refund credited.")
        note = env["fix.credit.note"].search([("complaint_id", "=", c.id)])
        assert (note.invoice_id, note.amount, note.reason_code) == (invoice, 2000.0, "goodwill")
        assert note.state == "approved", "submitted into M20's own authority rule"
        [event] = _events(env, "complaint.concession_settled", c.id)
        assert '"settled": true' in event.payload

    def test_no_invoice_is_handed_off_as_an_event(self, env, make_user, agent, customer, ou):
        raiser = make_user()
        c = _approved_concession(env, make_user, raiser, customer, ou, 900.0, "refund")
        c = c.with_user(agent)
        _to_accepted(c, "Refund of BDT 900.")
        c.action_close("Refund promised.")
        assert "no service order" in c.concession_settlement_note
        [event] = _events(env, "complaint.concession_settled", c.id)
        assert '"settled": false' in event.payload and '"amount": 900.0' in event.payload


# ==========================================================================
# 5. Surveys and event consumers (M34-4, M34-6, M34-7, M34-10)
# ==========================================================================
class TestSurveysAndEvents:
    def test_a_closed_order_event_produces_the_survey(self, env, closed_order):
        publish(
            env,
            "service_order.closed",
            "fix.service.order",
            closed_order.id,
            {"order_id": closed_order.id},
        )
        _relay(env, "service_order.closed")
        survey = env["fix.survey"].search([("service_order_id", "=", closed_order.id)])
        assert len(survey) == 1 and survey.source_event_id
        # a replayed or foreign event is ignored, not raised
        assert (
            env["fix.survey"].consume_order_closed({"aggregate": "res.partner", "aggregate_id": 1})
            is None
        )
        assert env["fix.survey"].consume_order_closed({"aggregate_id": 0}) is None

    def test_a_rating_of_three_raises_a_recovery_task(self, env, closed_order):
        survey = env["fix.survey"].consume_order_closed({"aggregate_id": closed_order.id})
        survey.rating = "3"
        assert survey.nps_score == -100
        assert survey.followup_id and survey.followup_id.reason == "low_rating"
        survey4 = env["fix.survey"].consume_order_closed(
            {"aggregate_id": closed_order.copy({"state": "closed"}).id}
        )
        survey4.rating = "4"
        assert not survey4.followup_id

    def test_the_post_closure_survey_is_actually_sent(self, env, agent, customer, ou):
        c = _complaint(env, agent, customer, ou)
        _to_accepted(c)
        c.action_close("Repaired.")
        _relay(env, "complaint.post_closure_survey_dispatched")
        delivery = c.post_closure_delivery_id
        assert delivery and delivery.to_address == customer.phone
        assert delivery.source_model == "fix.complaint" and delivery.source_id == c.id
        event = _events(env, "complaint.post_closure_survey_dispatched", c.id)
        again = env["fix.complaint"].consume_post_closure_survey(event._relay_event_dict())
        assert again == delivery, "a redelivery must not queue a second message"

    def _stale(self, env, complaint):
        env.flush_all()
        env.cr.execute(
            "UPDATE fix_complaint SET create_date = now() - interval '80 hours' WHERE id = %s",
            (complaint.id,),
        )
        env.invalidate_all()

    def test_escalation_assigns_and_notifies_a_tier_4_holder(
        self, env, make_user, agent, customer, ou
    ):
        coo = make_user(TIER_GROUP["tier_4"])
        c = _complaint(env, agent, customer, ou)
        self._stale(env, c)
        assert env["fix.complaint"].cron_escalate_stale_complaints() >= 1
        assert c.escalation_owner_id == coo and c.quality_warning
        assert env["mail.activity"].search_count(
            [("res_model", "=", "fix.complaint"), ("res_id", "=", c.id), ("user_id", "=", coo.id)]
        )
        _relay(env, "complaint.escalated_72h")
        task = env["fix.workflow.task"].search(
            [("res_model", "=", "fix.complaint"), ("res_id", "=", c.id)]
        )
        assert (task.task_type, task.assigned_user_id, task.state) == ("exception", coo, "pending")
        event = _events(env, "complaint.escalated_72h", c.id)
        env["fix.complaint"].consume_escalated_72h(event._relay_event_dict())
        assert (
            env["fix.workflow.task"].search_count(
                [("res_model", "=", "fix.complaint"), ("res_id", "=", c.id)]
            )
            == 1
        )
        with pytest.raises(UserError, match="changes only through its workflow"):
            c.with_user(agent).write({"escalation_owner_id": agent.id})

    def test_escalation_honours_the_named_user_and_reports_a_gap(
        self, env, make_user, agent, customer, ou
    ):
        named = make_user()
        env["ir.config_parameter"].set_param("cd_cx_feedback.escalation_user", named.login)
        c = _complaint(env, agent, customer, ou)
        self._stale(env, c)
        env["fix.complaint"].cron_escalate_stale_complaints()
        assert c.escalation_owner_id == named
        env["ir.config_parameter"].set_param("cd_cx_feedback.escalation_user", "")
        orphan = _complaint(env, agent, customer, ou)
        self._stale(env, orphan)
        if not orphan._escalation_owner():
            env["fix.complaint"].cron_escalate_stale_complaints()
            assert not orphan.escalation_owner_id
            assert "NOBODY could be notified" in orphan.message_ids[0].body
            task = env["fix.complaint"].consume_escalated_72h({"aggregate_id": orphan.id})
            assert not task.assigned_user_id and "no escalation owner" in task.name


# ==========================================================================
# 6. P03: every new action is whitelisted AND has a button
# ==========================================================================
def test_every_complaint_action_is_whitelisted_and_has_a_button(env):
    m34 = importlib.import_module("odoo.addons.cd_p03_portal.controllers.a03.m34")
    js = (Path(m34.__file__).resolve().parents[2] / "static" / "src" / "a03" / "m34.js").read_text(
        encoding="utf-8"
    )
    buttons = set(re.findall(r"m: '(action_\w+)'", js))
    expected = {
        "fix.complaint": {
            "action_take_ownership",
            "action_assign",
            "action_assess",
            "action_reassess",
            "action_investigate",
            "action_raise_ncr",
            "action_record_root_cause",
            "action_verify_root_cause",
            "action_open_capa",
            "action_request_verification",
            "action_request_approval",
            "action_recall_approval",
            "action_respond",
            "action_customer_accept",
            "action_customer_reject",
            "action_close",
            "action_decline",
            "action_reopen",
        },
        "fix.cx.followup": {"action_close_recovered", "action_raise_complaint"},
    }
    for model, actions in expected.items():
        assert actions <= m34.SURFACES[model]["actions"], model
        assert actions <= buttons, sorted(actions - buttons)
        for name in actions:
            assert callable(getattr(env[model], name)), name
