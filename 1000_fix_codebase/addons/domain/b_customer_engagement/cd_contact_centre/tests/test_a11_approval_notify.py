"""A11 audit P2: the M63 engine publishes approval.* events and nobody told
the approver. These tests prove the whole wire: the shipped consumer rows
(the data XML itself is loaded here, in the rolled-back test transaction),
the relay-only guard, the e-mail + SMS to each approver through the one
exit (fix.notif.delivery.queue), dedup on re-relay, and the reminder /
escalated / decided notices.

Reuses the E1-E4 fixture shapes (fix.complaint is the concession-domain
routable record; <=1,000 is Tier 1).
"""

import json

import pytest
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError
from odoo.tools import convert_file

T1 = "cd_entity_config.group_dofa_tier_1"
T2 = "cd_entity_config.group_dofa_tier_2"


def _user(env, login, groups=()):
    existing = env["res.users"].search([("login", "=", login)], limit=1)
    if existing:
        return existing
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    ou = env["operating.unit"].search([], limit=1)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, gids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    # The approver must be reachable on both channels for the wire to be
    # provable; a user with no address is covered by its own test below.
    # `mobile` is not on res.partner in this Odoo build; SMS resolves
    # through the partner's phone.
    user.partner_id.write({"email": "%s@1000fix.test" % login, "phone": "+8801700000101"})
    env["hr.employee"].create({"name": login, "user_id": user.id})
    return user


@pytest.fixture
def c(odoo_env):
    if "fix.complaint" not in odoo_env:
        pytest.skip("cd_cx_feedback is not installed")
    env = odoo_env
    # The shipped data file, loaded the way an upgrade loads it. It runs in
    # the test transaction, so the rows vanish with the rollback — but the
    # file itself is the artefact under test.
    convert_file(
        env,
        "cd_contact_centre",
        "data/fix_approval_notify_consumers.xml",
        {},
        mode="init",
    )
    x = type("Ctx", (), {})()
    x.env = env
    x.ou = env["operating.unit"].search([], limit=1)
    x.clerk = _user(env, "a11_notify_clerk")
    x.t1 = _user(env, "a11_notify_t1", [T1])
    x.customer = env["res.partner"].create({"name": "A11 Notify Customer"})
    return x


def _complaint(c, user=None):
    return (
        c.env["fix.complaint"]
        .with_user(user or c.clerk)
        .create(
            {
                "name": "A11N-%s" % (user or c.clerk).login,
                "customer_id": c.customer.id,
                "operating_unit_id": c.ou.id,
                "description": "approver-notify probe",
                "severity": "minor",
                "concession_amount": 800.0,
                "concession_type": "refund",
                "dofa_justification": "Approver notification probe.",
            }
        )
    )


def _request(c, record):
    """Route the record; the approver must exist BEFORE the request (approvers
    resolve at request time). The clerk is the requester."""
    record.with_user(c.clerk).action_request_approval(justification="Approver notification probe.")
    assert record.approval_state == "pending"
    return record.approval_request_id


def _delivered(c, user):
    return c.env["fix.notif.delivery"].search(
        [
            ("partner_id", "=", user.partner_id.id),
            ("source_model", "=", "fix.approval.request"),
        ]
    )


def _event(env, event_type, rec):
    return (
        env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", event_type), ("aggregate_id", "=", rec.id)], limit=1)
    )


class TestRequestedNotifiesTheApprovers:
    def test_the_wire_end_to_end_e_mail_and_sms(self, c):
        env = c.env
        rec = _complaint(c)
        req = _request(c, rec)
        # The publish happened; the relay hands it to the shipped consumers.
        event = _event(env, "approval.requested", rec)
        assert event, "the engine published no approval.requested event"
        env["fix.event.outbox"].sudo().cron_relay()
        deliveries = _delivered(c, c.t1)
        channels = sorted(d.channel for d in deliveries)
        assert channels == ["email", "sms"], "approver gets e-mail AND SMS, got %s" % channels
        assert all(d.state != "suppressed" for d in deliveries)
        for d in deliveries:
            assert req.name in d.body
            assert "inbox" in d.body
            assert d.purpose == "service_updates"
            assert d.lawful_basis == "contract"
            assert d.source_event_id == event.event_id

    def test_a_replayed_event_does_not_duplicate_the_notice(self, c):
        env = c.env
        rec = _complaint(c)
        _request(c, rec)
        outbox = env["fix.event.outbox"].sudo()
        outbox.cron_relay()
        before = len(_delivered(c, c.t1))
        outbox.cron_relay()
        outbox.cron_relay()
        assert len(_delivered(c, c.t1)) == before

    def test_an_approver_with_no_address_is_skipped_not_dead_lettered(self, c):
        env = c.env
        bare = _user(env, "a11_notify_bare", [T1])
        bare.partner_id.write({"email": False, "phone": False})
        rec = _complaint(c)
        req = _request(c, rec)
        # The recipients come from the event payload, so this is independent
        # of which tier-1 holder the engine actually routed to.
        result = env["fix.notif.delivery"].consume_approval_requested(
            {
                "event_id": "evt-a11-bare-1",
                "payload": {"request": req.name, "approver_ids": [bare.id]},
            }
        )
        assert result["queued"] == 0
        assert len(result["skipped"]) == 2, "one skip per channel: %s" % result["skipped"]
        assert not _delivered(c, bare)

    def test_the_consumers_refuse_a_direct_call(self, c):
        env = c.env
        with pytest.raises(AccessError, match="relay"):
            env["fix.notif.delivery"].with_user(c.clerk).consume_approval_requested({})
        with pytest.raises(AccessError, match="relay"):
            env["fix.notif.delivery"].with_user(c.t1).consume_approval_decided({})


class TestReminderEscalatedDecided:
    def test_the_reminder_goes_to_the_pending_assignee(self, c):
        env = c.env
        rec = _complaint(c)
        req = _request(c, rec)
        result = env["fix.notif.delivery"].consume_approval_reminder(
            {"event_id": "evt-a11-reminder", "payload": {"request": req.name}}
        )
        assert result["queued"] >= 1
        assert _delivered(c, c.t1).filtered(lambda d: "OVERDUE" in d.body)

    def test_the_escalation_goes_to_the_new_targets(self, c):
        env = c.env
        t2 = _user(env, "a11_notify_t2", [T2])
        rec = _complaint(c)
        req = _request(c, rec)
        result = env["fix.notif.delivery"].consume_approval_escalated(
            {
                "event_id": "evt-a11-escalated",
                "payload": {"request": req.name, "level": 2, "to": [t2.id]},
            }
        )
        assert result["queued"] >= 1
        deliveries = _delivered(c, t2)
        assert deliveries and all("escalated" in d.body for d in deliveries)

    def test_the_decision_closes_the_loop_with_the_requester(self, c):
        env = c.env
        rec = _complaint(c)
        _request(c, rec)
        task = approve_via_inbox(rec, c.t1, comment="Concession granted.")
        decided = _event(env, "approval.decided", rec)
        assert decided, "the engine published no approval.decided event"
        payload = json.loads(decided.payload or "{}")
        result = env["fix.notif.delivery"].consume_approval_decided(
            {"event_id": decided.event_id, "payload": payload}
        )
        assert result["queued"] >= 1
        mine = _delivered(c, c.clerk)
        assert mine and all("approved" in d.body for d in mine)
        assert task.assigned_user_id == c.t1


class TestTheShippedSubscriptions:
    def test_the_data_file_registers_all_four_consumers(self, c):
        env = c.env
        for xmlid, event_type, method in [
            (
                "consumer_approval_requested_notify_approvers",
                "approval.requested",
                "consume_approval_requested",
            ),
            (
                "consumer_approval_reminder_notify_approvers",
                "approval.reminder",
                "consume_approval_reminder",
            ),
            (
                "consumer_approval_escalated_notify_targets",
                "approval.escalated",
                "consume_approval_escalated",
            ),
            (
                "consumer_approval_decided_notify_requester",
                "approval.decided",
                "consume_approval_decided",
            ),
        ]:
            row = env.ref("cd_contact_centre.%s" % xmlid)
            assert row.event_type == event_type
            assert row.model == "fix.notif.delivery"
            assert row.method == method
            assert row.active, "an inactive subscription never fires"
