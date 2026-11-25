"""test_a03_w_merge_kyc_draft.py — A03 closing items W1, W4 and W5 for M33.

working/A03_Workflow_and_Approval_Report.md, "Also left": leads, complaints
and the rest were not re-pointed on a merge, and a merge reversal did not
unwind the re-points (W1); merge execution and KYC verification were not
routed through the M63 engine (W4); the draft-party switch was not called
by the modules that use a party (W5).

Every decision is taken by a NON-ADMIN user: a clerk requests, a data
steward decides from the approval inbox. The superuser only builds fixtures.
The consumers run the way they run in production: `publish` puts the event
in the outbox, `cron_relay()` delivers it, with this test's subscriptions
starting just before the test transaction.
"""

from datetime import timedelta

import pytest
from odoo.addons.cd_partner.tests.m40_fixtures import make_onboardable
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

REFUSED = (UserError, ValidationError, AccessError)
STEWARD = "cd_party_master.group_party_data_steward"
LM = "cd_party_master.group_party_registration_lm"
ADMIN = "cd_party_master.group_party_registration_admin"
CONTACTS = "base.group_partner_manager"
# A04 audit (2026-11-04) M40: fix.partner is written by the channel roles only.
CHANNEL_OFFICER = "cd_partner.group_fix_channel_officer"
CHANNEL_MANAGER = "cd_partner.group_fix_channel_manager"
ACCOUNTANT = "account.group_account_user"
POLICY = "cd_party_master.draft_party_policy"
GATE = "cannot be used for"


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def make_user(env):
    counter = {"n": 0}

    def _make(*xmlids):
        counter["n"] += 1
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "W Merge Probe %d" % counter["n"],
                    "login": "w.merge.probe.%d@a03.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def people(make_user):
    return {
        "clerk": make_user(CONTACTS),
        "steward": make_user(CONTACTS, STEWARD),
    }


PARTY_EVENTS = (
    "party.merged",
    "party.merge_reversed",
    "loyalty.merge_reversal_blocked",
    "loyalty.merge_reversal_shortfall",
)


def _relay(env):
    """Deliver this test's party events. The other subscriptions sit out;
    the party ones start just before this transaction (no backlog)."""
    Consumer = env["fix.event.consumer"].sudo()
    mine = Consumer.search([("event_type", "in", PARTY_EVENTS)])
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": env.cr.now() - timedelta(minutes=1)})
    return env["fix.event.outbox"].cron_relay()


def _execute(merge, people):
    """The clerk requests the merge; the steward executes it from the inbox."""
    approve_via_inbox(merge, people["steward"], requester=people["clerk"])
    assert merge.state == "executed" and merge.executed_by == people["steward"]
    return merge


def _logs(env, merge, **filters):
    domain = [("merge_id", "=", merge.id)] + [(k, "=", v) for k, v in filters.items()]
    return env["fix.party.repoint.log"].sudo().search(domain)


def _ou(env):
    return env["operating.unit"].search([], limit=1)


# ==========================================================================
# W1. Every open reference follows the merge, and the reversal unwinds it
# ==========================================================================
@pytest.fixture
def world(env):
    ou = _ou(env)
    Partner = env["res.partner"]
    victim = Partner.create({"name": "W1 Victim Co", "is_company": True, "phone": "01733300001"})
    survivor = Partner.create(
        {"name": "W1 Survivor Co", "is_company": True, "phone": "01733300001"}
    )
    third = Partner.create({"name": "W1 Third Party"})
    w = {"victim": victim, "survivor": survivor, "third": third}
    w["child"] = Partner.create({"name": "W1 Contact Person", "parent_id": victim.id})
    Lead = env["crm.lead"]
    w["lead_open"] = Lead.create({"name": "W1 open deal", "partner_id": victim.id})
    w["lead_lost"] = Lead.create({"name": "W1 lost deal", "partner_id": victim.id})
    w["lead_lost"].write(
        {
            "active": False,
            "probability": 0,
            "competitor": "W1 Rival",
            "lost_reason_code": "PRICE",
        }
    )
    Complaint = env["fix.complaint"]
    base = {
        "customer_id": victim.id,
        "operating_unit_id": ou.id,
        "description": "W1 merge probe",
        "severity": "minor",
    }
    w["complaint_open"] = Complaint.create({**base, "name": "W1 open complaint"})
    w["complaint_closed"] = Complaint.create({**base, "name": "W1 closed complaint"})
    w["complaint_closed"]._guarded().write({"state": "closed"})
    Conversation = env["fix.conversation"]
    conv = {"channel": "voice", "operating_unit_id": ou.id, "customer_id": victim.id}
    w["conv_open"] = Conversation.create(conv)
    w["conv_done"] = Conversation.create(conv)
    w["conv_done"]._guarded().write({"state": "resolved_agent"})
    w["credit"] = env["fix.credit.profile"].create({"customer_id": victim.id})
    w["biz_partner"] = env["fix.partner"].create(
        {"name": "W1 Referral", "partner_id": victim.id, "partner_type": "referral"}
    )
    w["estate"] = env["fix.device.estate"].create({"name": "W1 Estate", "client_id": victim.id})
    brand = env["fix.brand"].create({"name": "W1 Brand", "code": "W1BR"})
    model = env["fix.device.model"].create({"name": "W1 Phone", "brand_id": brand.id})
    w["device"] = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": victim.id, "serial_number": "W1-MERGE-1"}
    )
    policy = env["fix.sla.policy"].create(
        {
            "code": "W1-SLA",
            "name": "W1 SLA",
            "service_type": "walk_in",
            "priority": "normal",
            "response_hours": 2.0,
            "resolution_hours": 24.0,
        }
    )
    w["clock"] = env["fix.sla.kpi.instance"].start_for(
        w["complaint_open"], policy, "first_response", partner=victim
    )
    w["rights"] = env["fix.rights.request"].create(
        {"partner_id": victim.id, "request_type": "access"}
    )
    w["merge"] = env["fix.party.merge"].create({"survivor_id": survivor.id, "victim_id": victim.id})
    return w


# (fixture key, field, follows the merge?)
_FOLLOWS = [
    ("child", "parent_id", True),
    ("lead_open", "partner_id", True),
    ("lead_lost", "partner_id", False),
    ("complaint_open", "customer_id", True),
    ("complaint_closed", "customer_id", False),
    ("conv_open", "customer_id", True),
    ("conv_done", "customer_id", False),
    ("credit", "customer_id", True),
    ("biz_partner", "partner_id", True),
    ("estate", "client_id", True),
    ("device", "owner_id", True),
    ("clock", "partner_id", True),
    ("rights", "partner_id", True),
]


class TestMergeRepointsAndReversal:
    def test_the_consumers_are_registered(self, env):
        Consumer = env["fix.event.consumer"]
        merged = set(Consumer.search([("event_type", "=", "party.merged")]).mapped("model"))
        assert merged >= {
            "res.partner",
            "crm.lead",
            "fix.complaint",
            "fix.conversation",
            "fix.credit.profile",
            "fix.partner",
            "fix.device.estate",
            "fix.device",
            "fix.service.order",
            "fix.sla.kpi.instance",
            "fix.loyalty.account",
            "fix.party.duplicate",
            "fix.rights.request",
            "fix.segment.membership",
        }
        reversed_ = Consumer.search([("event_type", "=", "party.merge_reversed")])
        assert {(c.model, c.method) for c in reversed_} >= {
            ("fix.party.repoint.log", "consume_party_merge_reversed"),
            ("fix.loyalty.account", "consume_party_merge_reversed"),
        }

    def test_open_records_follow_history_stays_and_every_move_is_logged(self, env, world, people):
        _execute(world["merge"], people)
        _relay(env)
        victim, survivor = world["victim"], world["survivor"]
        for key, field, follows in _FOLLOWS:
            record = world[key].with_context(active_test=False)
            record.invalidate_recordset()
            expected = survivor if follows else victim
            assert record[field] == expected, "%s.%s should be on %s" % (
                key,
                field,
                expected.name,
            )
        logs = _logs(env, world["merge"])
        moved = {(log.res_model, log.res_id) for log in logs}
        for key, _field, follows in _FOLLOWS:
            assert ((world[key]._name, world[key].id) in moved) == follows, key
        assert set(logs.mapped("from_partner_id")) == {victim}
        assert set(logs.mapped("to_partner_id")) == {survivor}
        assert not any(logs.mapped("reversed"))

    def test_a_second_delivery_moves_and_logs_nothing(self, env, world, people):
        _execute(world["merge"], people)
        _relay(env)
        before = len(_logs(env, world["merge"]))
        event = (
            env["fix.event.outbox"]
            .search([("event_type", "=", "party.merged")], order="id desc", limit=1)
            ._relay_event_dict()
        )
        for model in (
            "res.partner",
            "crm.lead",
            "fix.complaint",
            "fix.conversation",
            "fix.credit.profile",
            "fix.partner",
            "fix.device.estate",
            "fix.sla.kpi.instance",
        ):
            assert env[model].sudo().consume_party_merged(event) == 0, model
        assert len(_logs(env, world["merge"])) == before

    def test_the_reversal_restores_what_still_points_at_the_survivor(
        self, env, world, people, make_user
    ):
        _execute(world["merge"], people)
        _relay(env)
        # After the merge, a channel officer re-points the business-partner
        # record to a third party: the reversal must not undo that decision.
        officer = make_user(CONTACTS, CHANNEL_OFFICER)
        world["biz_partner"].with_user(officer).write({"partner_id": world["third"].id})
        world["merge"].with_user(people["steward"]).action_reverse()
        _relay(env)
        victim = world["victim"]
        for key, field, _follows in _FOLLOWS:
            if key == "biz_partner":
                continue
            record = world[key].with_context(active_test=False)
            record.invalidate_recordset()
            assert record[field] == victim, "%s.%s was not restored" % (key, field)
        assert world["biz_partner"].partner_id == world["third"]
        logs = _logs(env, world["merge"])
        assert all(logs.mapped("reversed"))
        left = logs.filtered(lambda log: log.reversal_outcome == "left")
        assert (left.res_model, left.res_id) == ("fix.partner", world["biz_partner"].id)
        assert "left alone" in left.reversal_note
        assert set((logs - left).mapped("reversal_outcome")) == {"restored"}
        # Idempotent: the reversal again changes nothing.
        event = (
            env["fix.event.outbox"]
            .search([("event_type", "=", "party.merge_reversed")], order="id desc", limit=1)
            ._relay_event_dict()
        )
        again = env["fix.party.repoint.log"].sudo().consume_party_merge_reversed(event)
        assert again["restored"] == again["left"] == 0

    def test_a_merge_reversed_before_delivery_moves_nothing(self, env, world, people):
        _execute(world["merge"], people)
        world["merge"].with_user(people["steward"]).action_reverse()
        _relay(env)
        assert world["lead_open"].partner_id == world["victim"]
        assert not _logs(env, world["merge"])

    def test_a_forged_event_moves_nothing(self, env, world, people):
        """The merge record is the authority, not the payload."""
        _execute(world["merge"], people)
        victim, third = world["victim"], world["third"]
        forged = {"survivor_id": third.id, "victim_id": victim.id, "merge_id": world["merge"].id}
        assert env["crm.lead"].sudo().consume_party_merged({"payload": forged}) == 0
        assert env["fix.complaint"].sudo().consume_party_merged({"payload": forged}) == 0
        assert world["lead_open"].partner_id == victim
        # Through the outbox: a forged merge names a third party as survivor,
        # and a forged reversal arrives while the merge still stands.
        publish(env, "party.merged", "res.partner", third.id, forged)
        publish(
            env,
            "party.merge_reversed",
            "res.partner",
            third.id,
            {"survivor_id": third.id, "restored_id": victim.id, "merge_id": world["merge"].id},
        )
        _relay(env)
        logs = _logs(env, world["merge"])
        assert logs and set(logs.mapped("to_partner_id")) == {world["survivor"]}
        assert not any(logs.mapped("reversed"))
        assert world["lead_open"].partner_id == world["survivor"]
        with pytest.raises(AccessError):
            env["fix.party.repoint.log"].with_user(people["clerk"]).consume_party_merge_reversed(
                {"payload": {"merge_id": world["merge"].id}}
            )

    def test_the_log_is_append_only(self, env, world, people):
        _execute(world["merge"], people)
        _relay(env)
        log = _logs(env, world["merge"])[:1]
        Log = env["fix.party.repoint.log"]
        for actor in (Log.with_user(people["steward"]), Log.sudo()):
            with pytest.raises(UserError):
                actor.browse(log.id).write({"reversed": True})
            with pytest.raises(UserError):
                actor.browse(log.id).unlink()
            with pytest.raises(UserError):
                actor.create(
                    {
                        "merge_id": world["merge"].id,
                        "res_model": "crm.lead",
                        "res_id": world["lead_lost"].id,
                        "field_name": "partner_id",
                        "from_partner_id": world["victim"].id,
                        "to_partner_id": world["survivor"].id,
                        "at": "2026-01-01 00:00:00",
                    }
                )
        # repoint() is server code only (@api.private), never an RPC method.
        assert getattr(type(Log).repoint, "_api_private", False)

    def test_a_survivor_with_its_own_credit_profile_keeps_both(self, env, world, people):
        world["credit"].write({"credit_hold": True, "hold_reason": "W1 overdue"})
        own = env["fix.credit.profile"].create({"customer_id": world["survivor"].id})
        _execute(world["merge"], people)
        _relay(env)
        assert world["credit"].customer_id == world["victim"]
        assert own.customer_id == world["survivor"]
        note = own.message_ids.filtered(lambda m: "Party merge #%s" % world["merge"].id in m.body)
        assert note and "ON HOLD" in note[0].body


# ==========================================================================
# W1.4 Loyalty: the merge transfer is reversed by posted counter-lines
# ==========================================================================
@pytest.fixture
def program(env):
    program = env["fix.loyalty.program"].create(
        {"name": "W1 Privilege", "code": "W1LOY", "points_per_bdt": 0.01, "bdt_per_point": 0.5}
    )
    env["fix.loyalty.tier"].create(
        {"program_id": program.id, "name": "W1 Silver", "code": "W1SILVER", "sequence": 1}
    )
    return program


def _credit(env, account, points):
    line = env["fix.loyalty.ledger"].create(
        {"account_id": account.id, "transaction_type": "accrual", "points": points}
    )
    line.action_post()
    return line


class TestLoyaltyReversal:
    def _pair(self, env, program):
        victim = env["res.partner"].create({"name": "W1 Loyal Victim"})
        survivor = env["res.partner"].create({"name": "W1 Loyal Survivor"})
        Account = env["fix.loyalty.account"]
        victim_acct = Account.create({"partner_id": victim.id, "program_id": program.id})
        target = Account.create({"partner_id": survivor.id, "program_id": program.id})
        merge = env["fix.party.merge"].create({"survivor_id": survivor.id, "victim_id": victim.id})
        return victim_acct, target, merge

    def test_the_transfer_is_undone_by_counter_lines_and_the_account_reopens(
        self, env, program, people
    ):
        victim_acct, target, merge = self._pair(env, program)
        original = _credit(env, victim_acct, 300)
        _credit(env, target, 100)
        _execute(merge, people)
        _relay(env)
        assert victim_acct.state == "closed" and victim_acct.points_balance == 0
        assert target.points_balance == 400
        transfer = env["fix.loyalty.merge.transfer"].search([("merge_id", "=", merge.id)])
        assert transfer.points == 300 and transfer.closed_victim and len(transfer.ledger_ids) == 2
        merge.with_user(people["steward"]).action_reverse()
        _relay(env)
        assert victim_acct.state == "active" and victim_acct.points_balance == 300
        assert target.points_balance == 100
        assert transfer.reversed and transfer.points_returned == 300
        counter = transfer.reversal_ledger_ids
        assert set(counter.mapped("state")) == {"posted"}
        assert sorted(counter.mapped("points")) == [-300, 300]
        # Posted lines are never edited: the transfer lines are as they were.
        assert set(transfer.ledger_ids.mapped("state")) == {"posted"}
        assert sorted(transfer.ledger_ids.mapped("points")) == [-300, 300]
        assert (original.points, original.state) == (300, "posted")
        # Idempotent.
        event = (
            env["fix.event.outbox"]
            .search([("event_type", "=", "party.merge_reversed")], order="id desc", limit=1)
            ._relay_event_dict()
        )
        assert env["fix.loyalty.account"].sudo().consume_party_merge_reversed(event) == {
            "outcomes": []
        }
        assert victim_acct.points_balance == 300

    def test_points_already_spent_on_the_survivor_are_a_named_shortfall(
        self, env, program, people, make_user
    ):
        settler = make_user("cd_entity_config.group_dofa_tier_2")
        victim_acct, target, merge = self._pair(env, program)
        _credit(env, victim_acct, 300)
        _execute(merge, people)
        _relay(env)
        spend = env["fix.loyalty.ledger"].create(
            {"account_id": target.id, "transaction_type": "redemption", "points": -200}
        )
        spend.action_post()
        merge.with_user(people["steward"]).action_reverse()
        _relay(env)
        assert victim_acct.state == "active" and victim_acct.points_balance == 100
        assert target.points_balance == 0
        transfer = env["fix.loyalty.merge.transfer"].search([("merge_id", "=", merge.id)])
        assert transfer.points_returned == 100 and "shortfall" in transfer.reversal_note
        assert env["fix.event.outbox"].search_count(
            [("event_type", "=", "loyalty.merge_reversal_shortfall")]
        )
        # The alert has a reader: a Tier 2 holder is asked to settle the
        # 200-point shortfall by adjustment (FF-48 wiring, once per event).
        _relay(env)
        _relay(env)
        todo = victim_acct.activity_ids.filtered(lambda a: a.user_id == settler)
        assert len(todo) == 1 and "200-point shortfall" in (todo.note or "")

    def test_a_lone_account_is_re_pointed_and_given_back(self, env, program, people):
        victim = env["res.partner"].create({"name": "W1 Lone Victim"})
        survivor = env["res.partner"].create({"name": "W1 Lone Survivor"})
        acct = env["fix.loyalty.account"].create(
            {"partner_id": victim.id, "program_id": program.id}
        )
        merge = env["fix.party.merge"].create({"survivor_id": survivor.id, "victim_id": victim.id})
        _execute(merge, people)
        _relay(env)
        assert acct.partner_id == survivor
        assert _logs(env, merge, res_model="fix.loyalty.account", res_id=acct.id)
        merge.with_user(people["steward"]).action_reverse()
        _relay(env)
        assert acct.partner_id == victim


# ==========================================================================
# W4. Merge execution and KYC are decided from the M63 inbox
# ==========================================================================
class TestMergeIsRouted:
    def test_pressing_execute_is_refused_for_everyone(self, env, world, people):
        for user in (people["clerk"], people["steward"]):
            with pytest.raises(UserError, match="inbox"):
                world["merge"].with_user(user).action_execute()
        with pytest.raises(UserError):
            world["merge"].with_user(people["steward"]).write({"state": "executed"})
        assert world["merge"].state == "draft"

    def test_routing_excludes_requester_and_the_creators_of_either_party(
        self, env, make_user, people
    ):
        creator = make_user(CONTACTS, STEWARD)
        requester = make_user(CONTACTS, STEWARD)
        victim = env["res.partner"].with_user(creator).create({"name": "W4 Victim"})
        survivor = env["res.partner"].create({"name": "W4 Survivor"})
        merge = env["fix.party.merge"].create({"survivor_id": survivor.id, "victim_id": victim.id})
        merge.with_user(requester).action_request_approval()
        routed = assigned(merge)
        assert merge.approval_request_id.decision_domain == "party_merge"
        assert people["steward"] in routed
        assert creator not in routed and requester not in routed
        approve_via_inbox(merge, people["steward"])
        assert merge.state == "executed" and merge.approval_state == "approved"
        assert merge.executed_by == people["steward"]
        with pytest.raises(UserError, match="cannot be moved"):
            merge.with_user(requester).write(
                {"victim_id": env["res.partner"].create({"name": "X"}).id}
            )

    def test_changing_the_pair_voids_the_request(self, env, world, people):
        merge = world["merge"]
        merge.with_user(people["clerk"]).action_request_approval()
        request = merge.approval_request_id
        merge.with_user(people["clerk"]).write({"victim_id": world["third"].id})
        assert request.state == "voided" and merge.approval_state == "none"
        assert not inbox_task(merge, people["steward"])

    def test_the_steward_check_binds_inside_the_inbox(self, env, world, people):
        """A routed decision reaches action_execute through the engine's sudo
        request; losing the steward group after routing must still refuse."""
        world["merge"].with_user(people["clerk"]).action_request_approval()
        task = inbox_task(world["merge"], people["steward"])
        people["steward"].write({"group_ids": [(3, env.ref(STEWARD).id)]})
        with pytest.raises(UserError, match="Party Data Steward"):
            task.with_user(people["steward"]).action_approve()
        assert world["merge"].state == "draft"

    def test_a_rejected_merge_stays_draft(self, env, world, people):
        world["merge"].with_user(people["clerk"]).action_request_approval()
        task = inbox_task(world["merge"], people["steward"])
        task.with_user(people["steward"]).action_reject("Not the same customer")
        assert world["merge"].state == "draft" and world["merge"].approval_state == "rejected"
        assert world["victim"].party_status != "merged"


class TestKycIsRouted:
    def _doc(self, env, user):
        partner = env["res.partner"].create({"name": "W4 KYC Party"})
        return (
            env["fix.identity.document"]
            .with_user(user)
            .create({"partner_id": partner.id, "document_type": "passport"})
        )

    def test_submit_requests_and_a_steward_who_did_not_capture_decides(
        self, env, make_user, people
    ):
        capturer = make_user(CONTACTS, STEWARD)
        doc = self._doc(env, capturer)
        doc.with_user(capturer).action_kyc_submit()
        assert doc.approval_request_id.decision_domain == "kyc"
        assert people["steward"] in assigned(doc) and capturer not in assigned(doc)
        with pytest.raises(UserError, match="inbox"):
            doc.with_user(people["steward"]).action_kyc_verify()
        approve_via_inbox(doc, people["steward"])
        assert doc.verification_status == "verified" and doc.verified_by == people["steward"]
        # Editing what was verified withdraws both the verification and its approval.
        doc.with_user(capturer).write({"document_type": "tin"})
        assert doc.verification_status == "unverified" and doc.approval_state == "none"

    def test_the_four_eyes_check_binds_inside_the_inbox(self, env, people):
        """Even if the capturer were handed the task, the apply refuses."""
        doc = self._doc(env, people["clerk"])
        doc.with_user(people["clerk"]).action_kyc_submit()
        task = inbox_task(doc, people["steward"])
        # Test surgery: the capturer becomes the record's creator after routing.
        env.cr.execute(
            "UPDATE fix_identity_document SET create_uid = %s WHERE id = %s",
            (people["steward"].id, doc.id),
        )
        doc.invalidate_recordset()
        with pytest.raises(UserError, match="Segregation"):
            task.with_user(people["steward"]).action_approve()
        assert doc.verification_status == "pending"

    def test_editing_a_pending_document_voids_the_request(self, env, people):
        doc = self._doc(env, people["clerk"])
        doc.with_user(people["clerk"]).action_kyc_submit()
        request = doc.approval_request_id
        doc.with_user(people["clerk"]).write({"document_type": "tin"})
        assert request.state == "voided" and doc.approval_state == "none"
        assert doc.verification_status == "unverified"
        assert not inbox_task(doc, people["steward"])

    def test_with_no_steward_the_submission_waits_and_says_why(self, env, make_user):
        clerk = make_user(CONTACTS)
        others = env.ref(STEWARD).all_user_ids - clerk
        if others:
            pytest.skip("this database has data stewards: %s" % others.mapped("login"))
        doc = self._doc(env, clerk)
        doc.with_user(clerk).action_kyc_submit()
        assert doc.verification_status == "pending" and doc.approval_state == "none"
        assert any("not yet routed" in (m.body or "") for m in doc.message_ids)


class TestRegistrationChecksBindInsideTheInbox:
    def test_a_line_manager_who_loses_the_group_after_routing_is_refused(self, env, make_user):
        clerk, lm = make_user(CONTACTS), make_user(LM)
        make_user(ADMIN)
        partner = (
            env["res.partner"]
            .with_user(clerk)
            .create({"name": "W4 Dealer", "party_class": "dealer"})
        )
        approval = partner.approval_ids
        task = inbox_task(approval, lm)
        assert task
        lm.write({"group_ids": [(3, env.ref(LM).id)]})
        with pytest.raises(UserError, match="line-manager"):
            task.with_user(lm).action_approve()
        assert approval.lm_state == "pending"


# ==========================================================================
# W5. The draft-party switch at the downstream call sites
# ==========================================================================
@pytest.fixture
def parties(env):
    return {
        "draft individual": env["res.partner"].create({"name": "W5 Walk-in"}),
        "pending dealer": env["res.partner"].create(
            # Test BIN: a dealer invoice must state the buyer's BIN before
            # the party gate is reached (commercial document standard).
            {"name": "W5 Dealer Ltd", "party_class": "dealer", "vat": "000000000013"}
        ),
    }


@pytest.fixture
def sites(env, make_user):
    """Each W5 call site, as a callable taking the party, run by a plain user
    (partner onboarding by a channel manager: the A04 M40 role, not the gate)."""
    clerk = make_user(CONTACTS)
    channel_manager = make_user(CONTACTS, CHANNEL_MANAGER)
    accountant = make_user(ACCOUNTANT)
    ou = _ou(env)
    branch = env["fix.branch"].search([], limit=1) or env["fix.branch"].create(
        {
            "name": "W5 Hub",
            "code": "W5-HUB",
            "entity_id": (
                env["fix.entity"].search([], limit=1)
                or env["fix.entity"].create(
                    {
                        "legal_name": "W5 Group Ltd",
                        "code": "W5GRP",
                        "company_id": env.company.id,
                        "operating_unit_id": ou.id,
                    }
                )
            ).id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "W5 Brand", "code": "W5BR"})
    model = env["fix.device.model"].create({"name": "W5 Phone", "brand_id": brand.id})
    program = env["fix.loyalty.program"].create(
        {"name": "W5 Loyalty", "code": "W5LOY", "points_per_bdt": 0.01, "bdt_per_point": 0.5}
    )
    env["ir.config_parameter"].sudo().set_param("cd_crm_ext.won_requires_approved_estimate", "0")
    serial = {"n": 0}

    def service_order(partner):
        serial["n"] += 1
        device = env["fix.device"].create(
            {
                "device_model_id": model.id,
                "owner_id": partner.id,
                "serial_number": "W5-%d" % serial["n"],
            }
        )
        env["fix.service.order"].with_user(clerk).create(
            {
                "device_id": device.id,
                "customer_id": partner.id,
                "branch_id": branch.id,
                "service_type": "walk_in",
                "order_category": "standard",
                "fault_description": "W5 gate probe",
            }
        )

    def won_deal(partner):
        env["crm.lead"].with_user(clerk)._check_won_gate(
            {
                "probability": 100,
                "partner_id": partner.id,
                "contract_ref": "PO-W5",
                "contract_verified": True,
            }
        )

    def conversion(partner):
        lead = env["crm.lead"].create(
            {"name": "W5 deal", "partner_id": partner.id, "contract_ref": "PO-W5"}
        )
        lead._guarded().write({"contract_verified": True, "rate_card_approved": True})
        env.cr.execute("UPDATE crm_lead SET probability = 100 WHERE id = %s", (lead.id,))
        lead.invalidate_recordset()
        lead.with_user(clerk).action_convert_to_service_order()

    def loyalty_enrolment(partner):
        env["fix.loyalty.account"].with_user(clerk).create(
            {"partner_id": partner.id, "program_id": program.id}
        )

    def loyalty_activation(partner):
        account = env["fix.loyalty.account"].search(
            [("partner_id", "=", partner.id), ("program_id", "=", program.id)]
        )
        assert account, "enrol the party before the ruling"
        account._guarded().write({"state": "suspended"})
        account.with_user(clerk).action_activate()

    def onboarding(partner):
        biz = env["fix.partner"].create(
            {"name": "W5 Referral", "partner_id": partner.id, "partner_type": "referral"}
        )
        # A04 M40-F11: onboarding needs a published programme, an agreement
        # in force and a done checklist; the party gate is what is probed.
        make_onboardable(env, biz)
        biz.with_user(channel_manager).action_onboard()

    def invoice(partner):
        inv = env["fix.ar.invoice"].create_manual_invoice(
            {"customer_id": partner.id, "operating_unit_id": ou.id},
            [
                {
                    "description": "W5 gate probe",
                    "taxable_amount": 100.0,
                    "vat_amount": 15.0,
                    "line_total": 115.0,
                }
            ],
            reason_code="W5 probe",
        )
        inv.with_user(accountant).action_issue()

    return {
        "a service order": service_order,
        "a won opportunity": won_deal,
        "a converted service order": conversion,
        "loyalty enrolment": loyalty_enrolment,
        "an active loyalty account": loyalty_activation,
        "partner onboarding": onboarding,
        "an invoice": invoice,
    }


SITES = [
    "a service order",
    "a won opportunity",
    "a converted service order",
    "loyalty enrolment",
    "an active loyalty account",
    "partner onboarding",
    "an invoice",
]


# Sites whose whole action completes on this fixture under 'allow'. The
# others stop later for reasons of their own (a device-less conversion, the
# Mushak register), which the test tells apart from the party gate.
COMPLETE_TODAY = {
    "a service order",
    "a won opportunity",
    "loyalty enrolment",
    "an active loyalty account",
    "partner onboarding",
}


def _set_policy(env, value):
    env["ir.config_parameter"].sudo().set_param(POLICY, value)


def _dealer_enrolled_before_registering(env, sites):
    """A pending dealer whose loyalty account predates its registration: a
    pending dealer cannot be enrolled under any policy."""
    partner = env["res.partner"].create({"name": "W5 Member Ltd"})
    partner._guarded().write({"party_status": "active"})
    sites["loyalty enrolment"](partner)
    partner.write({"party_class": "dealer"})
    assert partner.party_status == "pending_approval"
    return partner


@pytest.mark.parametrize("site", SITES)
@pytest.mark.parametrize("kind", ["draft individual", "pending dealer"])
def test_refuse_stops_the_site(env, sites, parties, site, kind):
    partner = parties[kind]
    if site == "an active loyalty account" and kind == "pending dealer":
        partner = _dealer_enrolled_before_registering(env, sites)
    elif site == "an active loyalty account":
        # The account exists from before the ruling; activating it is gated.
        sites["loyalty enrolment"](partner)
    _set_policy(env, "refuse")
    reason = "draft" if kind == "draft individual" else "registration approval is not complete"
    with pytest.raises(UserError, match="%s %s.*%s" % (GATE, site, reason)):
        sites[site](partner)


@pytest.mark.parametrize("site", SITES)
def test_allow_lets_a_draft_individual_through(env, sites, parties, site):
    kind = "draft individual"
    assert env["ir.config_parameter"].sudo().get_param(POLICY) == "allow"
    if site == "an active loyalty account":
        sites["loyalty enrolment"](parties[kind])
    if site in COMPLETE_TODAY:
        sites[site](parties[kind])  # goes through exactly as before the switch
        return
    try:
        with env.cr.savepoint():
            sites[site](parties[kind])
    except REFUSED as exc:
        # The site may refuse for its own reasons (no device, a missing BIN);
        # never because of the party gate.
        assert GATE not in str(exc), exc


# 2026-11-10 audit: 'allow' switched the whole gate off, so the registration
# approval was a side register and a blocked, blacklisted or merged party was
# refused nowhere. 'allow' relaxes the DRAFT individual only.
@pytest.mark.parametrize("site", SITES)
def test_allow_still_refuses_a_pending_dealer(env, sites, parties, site):
    assert env["ir.config_parameter"].sudo().get_param(POLICY) == "allow"
    dealer = parties["pending dealer"]
    if site == "an active loyalty account":
        dealer = _dealer_enrolled_before_registering(env, sites)
    assert dealer.party_status == "pending_approval"
    reason = "registration approval is not complete"
    with pytest.raises(UserError, match="%s %s.*%s" % (GATE, site, reason)):
        sites[site](dealer)


def test_allow_still_refuses_a_dealer_whose_registration_was_rejected(env, sites, parties):
    assert env["ir.config_parameter"].sudo().get_param(POLICY) == "allow"
    dealer = parties["pending dealer"]
    dealer.approval_ids.action_reject("trade licence expired")
    assert dealer.party_status == "draft"
    with pytest.raises(UserError, match="%s a service order.*registration is not approved" % GATE):
        sites["a service order"](dealer)


HARD_STATUSES = {
    "blocked": "it is blocked",
    "blacklisted": "it is blacklisted",
    "merged": "it was merged into another party",
}


@pytest.mark.parametrize("policy", ["allow", "warn", "refuse"])
@pytest.mark.parametrize("status", sorted(HARD_STATUSES))
def test_a_blocked_blacklisted_or_merged_party_is_refused_under_every_policy(
    env, sites, status, policy
):
    partner = env["res.partner"].create({"name": "W5 Was Good"})
    partner._guarded().write({"party_status": "active"})
    sites["loyalty enrolment"](partner)  # the account predates the status
    partner._guarded().write({"party_status": status})
    _set_policy(env, policy)
    for site in SITES:
        # the two CRM sites have a block check of their own, which answers first
        match = "%s %s.*%s|on credit hold or blocked" % (GATE, site, HARD_STATUSES[status])
        with pytest.raises(UserError, match=match), env.cr.savepoint():
            sites[site](partner)


def test_an_active_party_passes_under_refuse(env, sites, make_user):
    partner = env["res.partner"].create({"name": "W5 Active"})
    partner._guarded().write({"party_status": "active"})
    _set_policy(env, "refuse")
    sites["loyalty enrolment"](partner)
    sites["partner onboarding"](partner)
    assert env["fix.partner"].search([("partner_id", "=", partner.id)]).state == "onboarded"
