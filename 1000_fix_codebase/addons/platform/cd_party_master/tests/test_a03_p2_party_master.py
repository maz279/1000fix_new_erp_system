"""test_a03_p2_party_master.py — the A03 P2 repairs to M33, as NON-ADMIN users.

Report §4.5 and the P2 row "M33" (working/A03_Workflow_and_Approval_Report.md),
findings M33-1, -3, -5, -6, -7, -8, -9. Every control is checked both ways:
the bypass is refused, and the legitimate path still works. The superuser is
trusted by the guards, so it only sets fixtures up.
"""

from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
LM = "cd_party_master.group_party_registration_lm"
ADMIN = "cd_party_master.group_party_registration_admin"
STEWARD = "cd_party_master.group_party_data_steward"
DPO = "cd_party_master.group_party_dpo"
CONTACTS = "base.group_partner_manager"
T2 = "cd_entity_config.group_dofa_tier_2"
POLICY = "cd_party_master.draft_party_policy"


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
                    "name": "M33 P2 Probe %d" % counter["n"],
                    "login": "m33.p2.probe.%d@a03.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


def _events(env, event_type, res_id):
    return env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", res_id)]
    )


def _approve(record, user, comment=None):
    task = inbox_task(record, user)
    assert task, "%s has no task; routed to %s" % (user.name, assigned(record).mapped("name"))
    task.with_user(user).action_approve(comment=comment)
    return task


@pytest.fixture
def chain(env, make_user):
    """A clerk who registers dealers, and one holder of each step's group."""
    return {
        "clerk": make_user(CONTACTS),
        "lm": make_user(LM),
        "admin": make_user(ADMIN),
    }


def _dealer(env, clerk, name="P2 Dealer Ltd"):
    return env["res.partner"].with_user(clerk).create({"name": name, "party_class": "dealer"})


# ==========================================================================
# 1. Registration approval opens itself; only it sets pending_approval
# ==========================================================================
class TestRegistrationIsAutomatic:
    def test_a_dealer_opens_its_own_registration_approval(self, env, chain):
        partner = _dealer(env, chain["clerk"])
        approval = partner.approval_ids
        assert len(approval) == 1 and approval.party_class == "dealer"
        assert partner.party_status == "pending_approval"
        assert approval.create_uid == chain["clerk"]
        # routed at once to the line-manager group, never to the clerk
        assert approval.approval_state == "pending" and approval.current_step == "lm"
        assert chain["lm"] in assigned(approval)
        assert chain["clerk"] not in assigned(approval)
        assert chain["admin"] not in assigned(approval)

    @pytest.mark.parametrize("party_class", ["corporate", "government"])
    def test_corporate_and_government_open_one_too(self, env, chain, party_class):
        partner = (
            env["res.partner"]
            .with_user(chain["clerk"])
            .create({"name": "P2 %s" % party_class, "party_class": party_class})
        )
        assert partner.approval_ids.party_class == party_class
        assert partner.party_status == "pending_approval"

    def test_an_individual_opens_nothing(self, env, chain):
        partner = env["res.partner"].with_user(chain["clerk"]).create({"name": "P2 Walk-in"})
        assert not partner.approval_ids and partner.party_status == "draft"

    def test_reclassifying_a_party_opens_the_approval(self, env, chain):
        partner = env["res.partner"].with_user(chain["clerk"]).create({"name": "P2 Grows Up"})
        partner.with_user(chain["clerk"]).write({"party_class": "corporate"})
        assert partner.approval_ids.party_class == "corporate"
        assert partner.party_status == "pending_approval"
        # the class is frozen while its approval is in progress
        with pytest.raises(UserError, match="in progress"):
            partner.with_user(chain["clerk"]).write({"party_class": "individual"})

    def test_pending_approval_cannot_be_typed(self, env, chain):
        partner = env["res.partner"].with_user(chain["clerk"]).create({"name": "P2 Typist"})
        with pytest.raises(UserError, match="Pending Approval"):
            partner.with_user(chain["clerk"]).write({"party_status": "pending_approval"})
        # binds the superuser as well: the status must have an approval behind it
        with pytest.raises(UserError, match="Pending Approval"):
            partner.write({"party_status": "pending_approval"})
        with pytest.raises(UserError, match="Pending Approval"):
            env["res.partner"].create(
                {"name": "P2 Born Pending", "party_status": "pending_approval"}
            )
        with pytest.raises(UserError, match="starts as 'draft'"):
            env["res.partner"].with_user(chain["clerk"]).create(
                {"name": "P2 Born Active", "party_status": "active"}
            )

    def test_a_second_open_approval_is_refused(self, env, chain):
        partner = _dealer(env, chain["clerk"])
        with pytest.raises(UserError, match="already has"):
            env["fix.registration.approval"].with_user(chain["clerk"]).create(
                {"partner_id": partner.id, "party_class": "dealer"}
            )

    def test_an_approval_cannot_be_moved_to_another_party(self, env, chain):
        approval = _dealer(env, chain["clerk"]).approval_ids
        other = env["res.partner"].create({"name": "P2 Other"})
        with pytest.raises(UserError, match="cannot be moved"):
            approval.with_user(chain["clerk"]).write({"partner_id": other.id})

    def test_reactivation_does_not_short_cut_a_registration(self, env, chain, make_user):
        partner = _dealer(env, chain["clerk"])
        with pytest.raises(ValidationError, match="awaiting its registration"):
            partner.with_user(make_user(CONTACTS, T2)).action_reactivate_party("urgent dealer")


# ==========================================================================
# 2. Two steps, two requests, two different people (M63 engine)
# ==========================================================================
class TestRegistrationRunsThroughTheEngine:
    def test_full_chain_activates_the_party(self, env, chain):
        partner = _dealer(env, chain["clerk"])
        approval = partner.approval_ids
        first = approval.approval_request_id
        assert first.decision_domain == "party_registration"
        _approve(approval, chain["lm"])
        assert approval.lm_state == "approved" and approval.lm_decided_by == chain["lm"]
        second = approval.approval_request_id
        assert second != first and first.state == "approved"
        assert approval.approval_state == "pending" and approval.current_step == "admin"
        assert assigned(approval) == chain["admin"]
        assert partner.party_status == "pending_approval"
        _approve(approval, chain["admin"])
        assert approval.admin_state == "approved" and approval.admin_decided_by == chain["admin"]
        assert approval.approval_state == "approved"
        partner.invalidate_recordset()
        assert partner.party_status == "active"
        assert _events(env, "party.activated", partner.id)
        assert partner._fix_assert_party_usable("a service order") == ""

    def test_pressing_approve_on_the_record_is_refused(self, env, chain):
        approval = _dealer(env, chain["clerk"]).approval_ids
        for method in ("action_lm_approve", "action_admin_approve", "action_approve_step"):
            with pytest.raises(UserError, match="inbox"):
                getattr(approval.with_user(chain["lm"]), method)()
        with pytest.raises(UserError, match="inbox"):
            approval.with_user(chain["lm"]).action_reject("no")
        with pytest.raises(UserError):
            approval.with_user(chain["lm"]).write(
                {"lm_state": "approved", "admin_state": "approved"}
            )

    def test_one_person_holding_both_groups_decides_only_one_step(self, env, chain, make_user):
        both = make_user(LM, ADMIN)
        approval = _dealer(env, chain["clerk"]).approval_ids
        assert both in assigned(approval)
        _approve(approval, both)
        # the administrator round goes to the OTHER administrator only
        assert assigned(approval) == chain["admin"]
        assert not inbox_task(approval, both)
        assert both.name not in approval.approval_simulate()["approvers"]
        _approve(approval, chain["admin"])
        assert approval.lm_decided_by == both and approval.admin_decided_by == chain["admin"]

    def test_with_no_other_administrator_the_line_manager_step_does_not_pass(
        self, env, chain, make_user
    ):
        both = make_user(LM, ADMIN)
        # the only other administrator leaves the group
        chain["admin"].write({"group_ids": [(3, env.ref(ADMIN).id)]})
        approval = _dealer(env, chain["clerk"]).approval_ids
        task = inbox_task(approval, both)
        others = env.ref(ADMIN).all_user_ids - both
        if others:
            pytest.skip(
                "this database has other registration administrators: %s" % others.mapped("login")
            )
        with pytest.raises(UserError, match="No one can approve"):
            task.with_user(both).action_approve()

    def test_the_requester_is_never_routed_a_step(self, env, chain, make_user):
        clerk_lm = make_user(CONTACTS, LM)
        approval = _dealer(env, clerk_lm).approval_ids
        assert clerk_lm not in assigned(approval)
        _approve(approval, chain["lm"])
        assert clerk_lm not in assigned(approval)

    def test_inbox_rejection_returns_the_party_to_draft_and_it_stays_unusable(
        self, env, chain, make_user
    ):
        partner = _dealer(env, chain["clerk"])
        approval = partner.approval_ids
        _approve(approval, chain["lm"])
        task = inbox_task(approval, chain["admin"])
        with pytest.raises(UserError, match="State why"):
            task.with_user(chain["admin"]).action_reject()
        task.with_user(chain["admin"]).action_reject("Trade licence expired")
        assert approval.admin_state == "rejected" and approval.approval_state == "rejected"
        partner.invalidate_recordset()
        assert partner.party_status == "draft"
        with pytest.raises(UserError, match="registration is not approved"):
            partner._fix_assert_party_usable("a service order")
        with pytest.raises(ValidationError, match="awaiting its registration"):
            partner.with_user(make_user(CONTACTS, T2)).action_reactivate_party("override")
        # re-submission is a new approval
        again = (
            env["fix.registration.approval"]
            .with_user(chain["clerk"])
            .create({"partner_id": partner.id})
        )
        assert again.party_class == "dealer" and partner.party_status == "pending_approval"

    def test_the_requester_recalls_and_re_requests(self, env, chain):
        approval = _dealer(env, chain["clerk"]).approval_ids
        approval.with_user(chain["clerk"]).action_recall_approval()
        assert approval.approval_state == "none" and approval.lm_state == "pending"
        approval.with_user(chain["clerk"]).action_request_approval()
        assert approval.approval_state == "pending" and chain["lm"] in assigned(approval)


# ==========================================================================
# 1b. The draft-party switch and the usability helper
# ==========================================================================
class TestDraftPartyPolicy:
    def _set(self, env, value):
        env["ir.config_parameter"].sudo().set_param(POLICY, value)

    def test_default_allow_is_todays_behaviour(self, env):
        draft = env["res.partner"].create({"name": "P2 Draft"})
        assert env["ir.config_parameter"].sudo().get_param(POLICY) == "allow"
        assert draft._fix_assert_party_usable("a service order") == ""

    def test_warn_returns_the_warning(self, env):
        self._set(env, "warn")
        draft = env["res.partner"].create({"name": "P2 Draft Warn"})
        assert "draft" in draft._fix_assert_party_usable("a service order")

    def test_refuse_refuses_and_an_unknown_value_fails_closed(self, env):
        draft = env["res.partner"].create({"name": "P2 Draft Refuse"})
        for value in ("refuse", "maybe"):
            self._set(env, value)
            with pytest.raises(UserError, match="draft"):
                draft._fix_assert_party_usable("a service order")

    def test_blocked_and_merged_are_refused_whatever_the_policy(self, env):
        blocked = env["res.partner"].create({"name": "P2 Blocked", "party_status": "blocked"})
        with pytest.raises(UserError, match="blocked"):
            blocked._fix_assert_party_usable("a service order")

    def test_the_module_applies_it_to_segments_and_active_roles(self, env, make_user):
        self._set(env, "refuse")
        user = make_user(CONTACTS)
        draft = env["res.partner"].create({"name": "P2 Draft Seg"})
        segment = env["fix.segment"].create({"code": "P2-SEG", "name": "P2 Segment"})
        with pytest.raises(UserError, match="segment membership"):
            segment.with_user(user).action_add_members(partner_ids=[draft.id])
        with pytest.raises(UserError, match="active customer role"):
            env["fix.party.role"].with_user(user).create(
                {"partner_id": draft.id, "role_type": "customer", "role_status": "active"}
            )
        role = (
            env["fix.party.role"]
            .with_user(user)
            .create({"partner_id": draft.id, "role_type": "customer"})
        )
        with pytest.raises(UserError, match="active customer role"):
            role.write({"role_status": "active"})
        self._set(env, "allow")
        segment.with_user(user).action_add_members(partner_ids=[draft.id])
        assert segment.member_count == 1


# ==========================================================================
# 3. Steward and DPO groups
# ==========================================================================
def _merge_pair(env):
    victim = env["res.partner"].create({"name": "P2 Dup Old", "phone": "01712345001"})
    survivor = env["res.partner"].create({"name": "P2 Dup New", "phone": "01712345001"})
    cand = env["fix.party.duplicate"].create(
        {"party_a": victim.id, "party_b": survivor.id, "score": 95.0}
    )
    return victim, survivor, cand


class TestStewardGroup:
    def test_duplicate_decisions_need_the_steward(self, env, make_user):
        _victim, _survivor, cand = _merge_pair(env)
        clerk, steward = make_user(CONTACTS), make_user(CONTACTS, STEWARD)
        with pytest.raises(UserError, match="Party Data Steward"):
            cand.with_user(clerk).action_review()
        with pytest.raises(UserError, match="Party Data Steward"):
            cand.with_user(clerk).action_dismiss("not the same")
        with pytest.raises(UserError):
            cand.with_user(clerk).write({"state": "dismissed"})
        cand.with_user(steward).action_review()
        cand.with_user(steward).action_confirm()
        assert cand.state == "confirmed" and cand.reviewed_by == steward

    def test_merge_execution_and_reversal_need_the_steward(self, env, make_user):
        victim, survivor, _cand = _merge_pair(env)
        merge = env["fix.party.merge"].create({"survivor_id": survivor.id, "victim_id": victim.id})
        clerk, steward = make_user(CONTACTS), make_user(CONTACTS, STEWARD)
        # A03 audit W4: a direct press is refused, for the steward too; the
        # clerk requests and the steward decides from the inbox.
        for user in (clerk, steward):
            with pytest.raises(UserError, match="inbox"):
                merge.with_user(user).action_execute()
        approve_via_inbox(merge, steward, requester=clerk)
        assert merge.state == "executed" and merge.executed_by == steward
        with pytest.raises(UserError, match="Party Data Steward"):
            merge.with_user(clerk).action_reverse()
        merge.with_user(steward).action_reverse()
        assert merge.state == "reversed"


# ==========================================================================
# 4. KYC verification
# ==========================================================================
class TestKyc:
    def _doc(self, env, user):
        partner = env["res.partner"].create({"name": "P2 KYC Party"})
        return (
            env["fix.identity.document"]
            .with_user(user)
            .create({"partner_id": partner.id, "document_type": "passport", "is_primary": True})
        )

    def test_verification_is_a_stamped_four_eyes_steward_action(self, env, make_user):
        capturer = make_user(CONTACTS, STEWARD)
        verifier = make_user(CONTACTS, STEWARD)
        doc = self._doc(env, capturer)
        with pytest.raises(UserError):
            doc.with_user(capturer).write({"verification_status": "verified"})
        # A03 audit W4: submitting routes the verification to the steward
        # inbox, never to the capturer; a direct press is refused.
        doc.with_user(capturer).action_kyc_submit()
        assert doc.verification_status == "pending" and doc.approval_state == "pending"
        assert verifier in assigned(doc) and capturer not in assigned(doc)
        for user in (capturer, verifier, make_user(CONTACTS)):
            with pytest.raises(UserError, match="inbox"):
                doc.with_user(user).action_kyc_verify()
        _approve(doc, verifier)
        assert doc.verification_status == "verified" and doc.approval_state == "approved"
        assert doc.verified_by == verifier and doc.verified_at
        assert _events(env, "party.identity_verified", doc.id)
        with pytest.raises(UserError, match="inbox"):
            doc.with_user(verifier).action_kyc_fail("second thoughts")

    def test_a_failure_needs_a_reason_and_can_be_resubmitted(self, env, make_user):
        clerk = make_user(CONTACTS)
        doc = self._doc(env, clerk)
        steward = make_user(CONTACTS, STEWARD)
        doc.with_user(clerk).action_kyc_submit()
        task = inbox_task(doc, steward)
        with pytest.raises(UserError, match="State why"):
            task.with_user(steward).action_reject()
        task.with_user(steward).action_reject("Photo does not match")
        assert (
            doc.verification_status == "failed" and doc.verification_note == "Photo does not match"
        )
        assert doc.verified_by == steward and doc.approval_state == "rejected"
        doc.with_user(clerk).action_kyc_submit()
        assert doc.verification_status == "pending" and doc.approval_state == "pending"

    def test_editing_a_verified_document_voids_the_verification(self, env, make_user):
        capturer = make_user(CONTACTS)
        steward = make_user(CONTACTS, STEWARD)
        doc = self._doc(env, capturer)
        doc.with_user(capturer).action_kyc_submit()
        _approve(doc, steward)
        assert doc.verification_status == "verified"
        doc.with_user(capturer).write({"document_type": "tin"})
        assert doc.verification_status == "unverified" and not doc.verified_by


# ==========================================================================
# 5. Data-subject rights: DPO, state guard, the 30-day clock
# ==========================================================================
class TestRightsRequests:
    def _req(self, env, user=None, days_ago=0, **vals):
        partner = env["res.partner"].create({"name": "P2 Data Subject"})
        req = (
            env["fix.rights.request"]
            .with_user(user or env.user)
            .create({"partner_id": partner.id, "request_type": "access", **vals})
        )
        if days_ago:
            # Back-date receipt (test surgery): the clock reads statutory_due.
            received = fields.Datetime.now() - timedelta(days=days_ago)
            env.flush_all()
            env.cr.execute(
                "UPDATE fix_rights_request SET received_at = %s, statutory_due = %s WHERE id = %s",
                (received, (received + timedelta(days=30)).date(), req.id),
            )
            req.invalidate_recordset()
        return req

    def test_the_lifecycle_belongs_to_the_dpo(self, env, make_user):
        clerk, dpo = make_user(CONTACTS), make_user(CONTACTS, DPO)
        req = self._req(env, clerk)
        with pytest.raises(UserError, match="Data Protection Officer"):
            req.with_user(clerk).action_verify()
        with pytest.raises(UserError):
            req.with_user(clerk).write({"state": "fulfilled", "evidence_ref": "FORGED"})
        req.with_user(dpo).action_verify()
        req.with_user(dpo).action_start()
        req.with_user(dpo).action_fulfil(evidence="EXPORT-P2-1")
        assert req.state == "fulfilled" and req.evidence_ref == "EXPORT-P2-1"

    def test_verify_cannot_reopen_a_fulfilled_request(self, env, make_user):
        dpo = make_user(CONTACTS, DPO)
        req = self._req(env)
        req.with_user(dpo).action_verify()
        req.with_user(dpo).action_fulfil(evidence="EXPORT-P2-2")
        with pytest.raises(ValidationError, match="newly received"):
            req.with_user(dpo).action_verify()
        with pytest.raises(ValidationError, match="cannot be rejected"):
            req.with_user(dpo).action_reject("late basis")
        assert req.state == "fulfilled"

    def test_start_needs_a_verified_identity(self, env, make_user):
        dpo = make_user(CONTACTS, DPO)
        req = self._req(env)
        with pytest.raises(ValidationError, match="verified"):
            req.with_user(dpo).action_start()

    def test_the_clock_reminds_then_escalates_once_each(self, env, make_user):
        handler, dpo = make_user(CONTACTS), make_user(CONTACTS, DPO)
        due_soon = self._req(env, days_ago=25, handler_id=handler.id)
        overdue = self._req(env, days_ago=31)
        fresh = self._req(env)
        Req = env["fix.rights.request"]
        out = Req.cron_rights_request_clock()
        assert out["reminded"] >= 1 and out["escalated"] >= 1
        assert due_soon.reminded_at and not due_soon.escalated_at
        assert due_soon.activity_ids.filtered(lambda a: a.user_id == handler)
        assert _events(env, "rights_request.due_soon", due_soon.id)
        assert overdue.escalated_at
        assert overdue.activity_ids.filtered(lambda a: a.user_id == dpo)
        assert _events(env, "rights_request.overdue", overdue.id)
        assert not fresh.reminded_at and not fresh.escalated_at
        # a second run adds nothing
        before = len(due_soon.activity_ids) + len(overdue.activity_ids)
        Req.cron_rights_request_clock()
        assert len(due_soon.activity_ids) + len(overdue.activity_ids) == before
        assert len(_events(env, "rights_request.overdue", overdue.id)) == 1
        # a decided request is off the clock
        dpo_env = due_soon.with_user(dpo)
        dpo_env.action_verify()
        dpo_env.action_reject("Statutory retention override")
        assert not due_soon.escalated_at

    def test_the_clock_cron_is_scheduled(self, env):
        cron = env.ref("cd_party_master.ir_cron_rights_request_clock")
        assert cron.active and "cron_rights_request_clock" in cron.code


# ==========================================================================
# 6. party.merged consumers inside M33 (R8)
# ==========================================================================
def _merged_event(env, merge):
    event = env["fix.event.outbox"].search(
        [("event_type", "=", "party.merged"), ("aggregate_id", "=", merge.survivor_id.id)],
        order="id desc",
        limit=1,
    )
    assert event
    return event


class TestMergeConsumers:
    def _setup(self, env, make_user):
        victim, survivor, cand = _merge_pair(env)
        third = env["res.partner"].create({"name": "P2 Third", "phone": "01712345001"})
        other_cand = env["fix.party.duplicate"].create(
            {"party_a": third.id, "party_b": victim.id, "score": 80.0}
        )
        repeat_cand = env["fix.party.duplicate"].create(
            {"party_a": victim.id, "party_b": third.id, "score": 70.0}
        )
        open_req = env["fix.rights.request"].create(
            {"partner_id": victim.id, "request_type": "access"}
        )
        done_req = env["fix.rights.request"].create(
            {"partner_id": victim.id, "request_type": "portability"}
        )
        done_req._guarded().write({"state": "fulfilled", "evidence_ref": "OLD"})
        seg_a = env["fix.segment"].create({"code": "P2-A", "name": "Only victim"})
        seg_b = env["fix.segment"].create({"code": "P2-B", "name": "Both"})
        seg_a.action_add_members(partner_ids=[victim.id])
        seg_b.action_add_members(partner_ids=[victim.id, survivor.id])
        merge = env["fix.party.merge"].create({"survivor_id": survivor.id, "victim_id": victim.id})
        approve_via_inbox(merge, make_user(CONTACTS, STEWARD))  # A03 audit W4: routed
        return locals()

    def test_the_payload_keeps_its_keys_and_adds_the_merge(self, env, make_user):
        s = self._setup(env, make_user)
        payload = _merged_event(env, s["merge"])._relay_event_dict()["payload"]
        assert payload["survivor_id"] == s["survivor"].id and payload["victim_id"] == s["victim"].id
        assert payload["mandated_consumers"] == "all"
        assert payload["merge_id"] == s["merge"].id and payload["executed_at"]

    def test_consumers_repoint_open_records_and_are_idempotent(self, env, make_user):
        s = self._setup(env, make_user)
        event = _merged_event(env, s["merge"])._relay_event_dict()
        for model in ("fix.party.duplicate", "fix.rights.request", "fix.segment.membership"):
            assert env[model].consume_party_merged(event) > 0, model
            assert env[model].consume_party_merged(event) == 0, "%s is not idempotent" % model
        assert s["cand"].state == "merged"  # M33-8: the queue closes
        assert s["other_cand"].state in ("new", "reviewed") and s["survivor"] in (
            s["other_cand"].party_a | s["other_cand"].party_b
        )
        assert s["repeat_cand"].state == "merged"  # would duplicate the re-pointed pair
        assert s["open_req"].partner_id == s["survivor"]
        assert s["done_req"].partner_id == s["victim"]  # decided: the statutory record stays
        Membership = env["fix.segment.membership"]
        a = Membership.search([("segment_id", "=", s["seg_a"].id)])
        assert a.partner_id == s["survivor"] and not a.exited_at
        b_victim = Membership.search(
            [("segment_id", "=", s["seg_b"].id), ("partner_id", "=", s["victim"].id)]
        )
        assert b_victim.exited_at and s["seg_b"].member_count == 1

    def test_a_reversed_merge_is_not_repointed_by_a_late_delivery(self, env, make_user):
        s = self._setup(env, make_user)
        event = _merged_event(env, s["merge"])._relay_event_dict()
        s["merge"].with_user(make_user(CONTACTS, STEWARD)).action_reverse()
        assert env["fix.rights.request"].consume_party_merged(event) == 0
        assert s["open_req"].partner_id == s["victim"]

    def test_the_relay_delivers_party_merged_to_the_m33_consumers(self, env, make_user):
        Consumer = env["fix.event.consumer"]
        mine = Consumer.search(
            [("event_type", "=", "party.merged"), ("module", "=", "cd_party_master")]
        )
        # duplicates, rights requests, segments, and (A03 audit W1) child contacts
        assert len(mine) == 4
        # Only this test's events: the other consumers sit out, and ours start
        # just before this transaction.
        (Consumer.search([]) - mine).write({"active": False})
        mine.write({"active_from": env.cr.now() - timedelta(minutes=1)})
        s = self._setup(env, make_user)
        env["fix.event.outbox"].cron_relay()
        event = _merged_event(env, s["merge"])
        deliveries = env["fix.event.consumer.delivery"].search([("event_id", "=", event.id)])
        assert set(deliveries.mapped("state")) == {"done"} and len(deliveries) == 4
        assert s["open_req"].partner_id == s["survivor"] and s["cand"].state == "merged"
