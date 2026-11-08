"""test_a03_approval_bypass.py — every A03 approval control, attacked as a NON-ADMIN.

The A03 workflow audit (2026-11-03, working/A03_Workflow_and_Approval_Report.md)
found that the area's approval rules were sound inside their action methods
and worthless around them:

  S1  the DOFA tier was never stored for records an ordinary user created
      (@api.depends_context("uid") on a stored compute), so the real approver
      was refused and the downstream gate read NULL as tier_0 and passed;
  S2  state and approval fields were writable by any internal user, so a
      plain write() forged a Tier-4 approval and closed the record;
  S4  approvals were not re-checked where they mattered and did not pin the
      amount that was approved.

Every existing suite ran as the superuser, which is exactly why none of this
showed: superuser writes are trusted, and superuser creates stored the tier.
So every test here acts through `with_user()` on a freshly created user that
holds only the groups named. Each control is checked twice — the bypass is
refused, and the legitimate path still works — because a guard that also
blocks the real workflow would be "fixed" by switching it off.
"""

import pytest
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def make_user(env):
    """A user holding exactly base.group_user plus the named groups."""
    counter = {"n": 0}

    def _make(*xmlids):
        counter["n"] += 1
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Bypass Probe %d" % counter["n"],
                    "login": "bypass.probe.%d@a03.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


T2 = "cd_entity_config.group_dofa_tier_2"
T3 = "cd_entity_config.group_dofa_tier_3"
T4 = "cd_entity_config.group_dofa_tier_4"
T5 = "cd_entity_config.group_dofa_tier_5"


def rule_in_force(env, make_user, ladder, reference):
    """A12 X3 / M30-1: a DOFA ruling is two-person — a Tier 4 proposes and a
    DIFFERENT Tier 5 countersigns, each acting for themselves, exactly as the
    workspace does. A citation carries a number."""
    t5 = make_user(T5)
    reference = "%s-1" % reference
    ladder.with_user(make_user(T4)).action_propose_ruling(
        reference=reference, countersigned_by=t5.id
    )
    ladder.with_user(t5).action_countersign(reference=reference)


@pytest.fixture
def customer(env):
    return env["res.partner"].create({"name": "Bypass Customer", "phone": "01719000001"})


@pytest.fixture
def ou(env):
    return env["operating.unit"].search([], limit=1) or env["operating.unit"].create(
        {"name": "Bypass Unit", "code": "BYP"}
    )


def _stored_tier(env, record):
    env.flush_all()
    env.cr.execute("SELECT dofa_tier_required FROM %s WHERE id = %%s" % record._table, (record.id,))
    return env.cr.fetchone()[0]


def _complaint(env, user, customer, ou, **vals):
    base = {
        "name": "BYP-%s" % user.login,
        "customer_id": customer.id,
        "operating_unit_id": ou.id,
        "description": "bypass probe",
        "severity": "minor",
    }
    base.update(vals)
    return env["fix.complaint"].with_user(user).create(base)


# ==========================================================================
# S1 — the tier is stored for ordinary users, and the gate fails closed
# ==========================================================================
class TestTierIsStoredAndFailsClosed:
    def test_a_plain_users_complaint_stores_its_tier(self, env, make_user, customer, ou):
        raiser = make_user()
        c = _complaint(
            env, raiser, customer, ou, concession_amount=3000.0, concession_type="refund"
        )
        assert _stored_tier(env, c) == "tier_2", "S1: the column used to be NULL here"

    def test_a_plain_users_campaign_stores_its_tier(self, env, make_user):
        maker = make_user()
        camp = env["fix.campaign"].with_user(maker).create({"name": "BYP camp", "budget": 300000.0})
        assert _stored_tier(env, camp) == "tier_4"

    def test_a_second_person_can_now_actually_approve(self, env, make_user, customer, ou):
        raiser, approver = make_user(), make_user(T2)
        c = _complaint(
            env, raiser, customer, ou, concession_amount=3000.0, concession_type="refund"
        )
        env.invalidate_all()
        c.with_user(
            raiser
        ).dofa_justification = "Repeat failure on the same repair; goodwill refund."
        approve_via_inbox(c, approver, raiser)  # R7: decided from the inbox
        c = c.with_user(approver)
        assert c.dofa_approved and c.concession_approved
        assert c.dofa_approved_amount == 3000.0

    def test_an_unapproved_concession_does_not_close_on_the_flag_alone(
        self, env, make_user, customer, ou
    ):
        raiser = make_user()
        c = _complaint(
            env, raiser, customer, ou, concession_amount=3000.0, concession_type="refund"
        )
        with pytest.raises(REFUSED):
            # the Boolean was free to set and the gate passed on NULL tier
            c.write({"concession_approved": True})
        with pytest.raises(ValidationError):
            c.action_close("resolved")

    def test_a_zero_amount_needs_no_approval(self, env, make_user, customer, ou):
        c = _complaint(env, make_user(), customer, ou)
        assert c.dofa_tier_required == "tier_0"


# ==========================================================================
# S2 — approval and lifecycle fields cannot be written directly
# ==========================================================================
class TestFieldsCannotBeForged:
    def test_forging_a_dofa_approval_is_refused(self, env, make_user, customer, ou):
        raiser = make_user()
        c = _complaint(
            env, raiser, customer, ou, concession_amount=250000.0, concession_type="refund"
        )
        with pytest.raises(UserError, match="cannot be set directly"):
            c.write({"dofa_approved": True, "dofa_approved_tier": "tier_5"})

    def test_closing_a_critical_complaint_by_state_write_is_refused(
        self, env, make_user, customer, ou
    ):
        c = _complaint(env, make_user(), customer, ou, severity="critical")
        with pytest.raises(UserError):
            c.write({"state": "closed"})

    def test_creating_a_record_already_in_a_late_state_is_refused(
        self, env, make_user, customer, ou
    ):
        with pytest.raises(UserError):
            _complaint(env, make_user(), customer, ou, state="closed")

    def test_an_unchanged_echo_is_allowed(self, env, make_user, customer, ou):
        """The P03 form posts every field it shows; a no-op value must pass."""
        c = _complaint(env, make_user(), customer, ou)
        c.write({"state": "new", "description": "edited description"})
        assert c.description == "edited description"

    def test_a_context_flag_cannot_open_the_guard(self, env, make_user, customer, ou):
        """JSON-RPC callers choose their own context; the token is an object."""
        c = _complaint(env, make_user(), customer, ou)
        with pytest.raises(UserError):
            c.with_context(fix_guarded_transition=True).write({"state": "closed"})

    def test_the_complaint_lifecycle_still_runs_through_its_actions(
        self, env, make_user, customer, ou
    ):
        c = _complaint(env, make_user(), customer, ou)
        # A03 P2 (M34): the ISO 10002 lifecycle assesses first and closes
        # only once the customer has accepted the response.
        c.action_assess()
        c.action_investigate()
        assert c.state == "investigating"
        c.action_respond("We replaced the part.")
        c.action_customer_accept()
        c.action_close("Replaced the part and confirmed with the customer.")
        assert c.state == "closed"


# ==========================================================================
# S4 — the approval covers what was approved, where it is consumed
# ==========================================================================
class TestApprovalCoversWhatWasApproved:
    def test_raising_the_amount_within_the_tier_needs_reapproval(
        self, env, make_user, customer, ou
    ):
        raiser, approver = make_user(), make_user(T2)
        c = _complaint(
            env, raiser, customer, ou, concession_amount=3000.0, concession_type="refund"
        )
        c.with_user(raiser).dofa_justification = "Goodwill for a repeat failure."
        approve_via_inbox(c, approver, raiser)
        c = c.with_user(approver)
        c.with_user(raiser).write({"concession_amount": 4999.0})  # still tier_2
        # R4: the approval falls the moment the amount passes what was signed
        # off, not only when a gate next looks.
        assert not c.dofa_approved and not c.concession_approved
        assert "approval withdrawn" in c.message_ids[0].body
        with pytest.raises(ValidationError, match="DOFA approval"):
            c.with_user(raiser).action_close("closed")

    def test_lowering_the_amount_keeps_the_approval(self, env, make_user, customer, ou):
        raiser, approver = make_user(), make_user(T2)
        c = _complaint(
            env, raiser, customer, ou, concession_amount=3000.0, concession_type="refund"
        )
        c.with_user(raiser).dofa_justification = "Goodwill for a repeat failure."
        approve_via_inbox(c, approver, raiser)
        c = c.with_user(approver)
        c.with_user(raiser).write({"concession_amount": 2000.0})
        assert c.dofa_approved and c.concession_approved
        c.with_user(raiser)._dofa_assert_approved("Service recovery concession")

    def test_campaign_launch_rechecks_the_approval_against_the_budget(self, env, make_user):
        maker, director = make_user(), make_user(T3)
        camp = (
            env["fix.campaign"]
            .with_user(maker)
            .create(
                {
                    "name": "BYP launch",
                    "channel": "social",
                    "budget": 150000.0,
                    "budget_memo_ref": "MEMO-1",
                    "start_date": "2026-11-01",
                    "end_date": "2026-11-30",
                }
            )
        )
        camp.with_user(maker).dofa_justification = "Eid campaign, social only."
        approve_via_inbox(camp, director, maker)
        assert camp.budget_approved
        camp.with_user(maker).write({"budget": 5000000.0})
        assert not camp.budget_approved and not camp.dofa_approved
        with pytest.raises(UserError, match="Launch blocked.*Tier 4"):
            camp.with_user(maker).action_launch()

    def test_campaign_tiers_follow_the_ladder_in_force(self, env, make_user):
        """The 50,000 / 200,000 literals are gone: a ruled ladder moves them."""
        maker = make_user()
        camp = (
            env["fix.campaign"]
            .with_user(maker)
            .create(
                {
                    "name": "BYP ladder",
                    "channel": "social",
                    "budget": 30000.0,
                    "start_date": "2026-11-01",
                    "end_date": "2026-11-30",
                }
            )
        )
        assert camp._dofa_current_tier() == "tier_0"
        ladder = env["fix.dofa.ladder"].search(
            [("target_model", "=", "fix.campaign"), ("basis", "=", "dofa_matrix")], limit=1
        ) or env["fix.dofa.ladder"].create(
            {
                "name": "BYP campaign ruling",
                "target_model": "fix.campaign",
                "basis": "ruling",
                "threshold_ids": [
                    (0, 0, {"upper_bound": 25000.0, "tier": "tier_0"}),
                    (0, 0, {"upper_bound": 1e12, "tier": "tier_3"}),
                ],
            }
        )
        expected = next(
            b.tier for b in ladder.threshold_ids.sorted("upper_bound") if b.upper_bound >= 30000.0
        )
        rule_in_force(env, make_user, ladder, "BYP-CAMP-RULING")
        assert camp._dofa_current_tier() == expected
        if expected != "tier_0":
            with pytest.raises(UserError, match="Launch blocked"):
                camp.action_launch()

    def test_campaign_state_cannot_be_written_to_running(self, env, make_user):
        maker = make_user()
        camp = env["fix.campaign"].with_user(maker).create({"name": "BYP run", "budget": 1000.0})
        with pytest.raises(UserError):
            camp.write({"state": "running"})
        with pytest.raises(UserError):
            camp.write({"budget_approved": True})


# ==========================================================================
# M10 loyalty
# ==========================================================================
@pytest.fixture
def account(env, customer):
    program = env["fix.loyalty.program"].create(
        {"name": "BYP Programme", "code": "BYPPRG", "points_per_bdt": 0.01, "bdt_per_point": 0.5}
    )
    env["fix.loyalty.tier"].create(
        {"program_id": program.id, "name": "Base", "code": "BYPBASE", "sequence": 1}
    )
    return env["fix.loyalty.account"].create({"partner_id": customer.id, "program_id": program.id})


class TestLoyalty:
    def test_a_manual_accrual_cannot_mint_points_without_approval(self, env, make_user, account):
        clerk = make_user()
        line = (
            env["fix.loyalty.ledger"]
            .with_user(clerk)
            .create({"account_id": account.id, "transaction_type": "accrual", "points": 1000000})
        )
        assert line.dofa_tier_required == "tier_4"
        with pytest.raises(ValidationError):
            line.action_post()

    def test_a_small_manual_accrual_still_posts(self, env, make_user, account):
        clerk = make_user()
        line = (
            env["fix.loyalty.ledger"]
            .with_user(clerk)
            .create({"account_id": account.id, "transaction_type": "accrual", "points": 200})
        )
        line.action_post()
        assert line.state == "posted" and account.points_balance == 200

    def test_a_posted_line_cannot_be_edited(self, env, make_user, account):
        clerk = make_user()
        line = (
            env["fix.loyalty.ledger"]
            .with_user(clerk)
            .create({"account_id": account.id, "transaction_type": "accrual", "points": 100})
        )
        line.action_post()
        with pytest.raises(UserError, match="cannot be edited"):
            line.write({"points": 99999})

    def test_balance_and_state_cannot_be_written(self, env, make_user, account):
        clerk = make_user()
        with pytest.raises(UserError):
            account.with_user(clerk).write({"points_balance": 4242424})
        with pytest.raises(UserError):
            env["fix.loyalty.ledger"].with_user(clerk).create(
                {
                    "account_id": account.id,
                    "transaction_type": "accrual",
                    "points": 10,
                    "state": "posted",
                }
            )

    def test_a_frozen_wallet_is_not_released_by_reactivation(self, env, make_user, account):
        account._guarded().write({"state": "frozen"})
        clerk = make_user()
        with pytest.raises(UserError, match="frozen"):
            account.with_user(clerk).action_activate()
        # The release is routed through the M63 inbox (A03 P2 M10).
        approve_via_inbox(account, make_user(T2), clerk, justification="Investigated: genuine.")
        assert account.state == "active"

    def test_retiring_a_scheme_withdraws_its_approval(self, env, make_user, account):
        maker, director = make_user(), make_user(T3)
        scheme = (
            env["fix.loyalty.scheme"]
            .with_user(maker)
            .create(
                {
                    "name": "BYP Scheme",
                    "code": "BYPSCH",
                    "program_id": account.program_id.id,
                    "estimated_annual_cost": 120000.0,
                }
            )
        )
        with pytest.raises(UserError):
            scheme.write({"state": "active"})
        scheme.dofa_justification = "Approved in the Q4 marketing plan."
        approve_via_inbox(scheme, director, maker)
        scheme.with_user(director).action_retire()
        assert not scheme.dofa_approved


# ==========================================================================
# M33 party master
# ==========================================================================
class TestPartyMaster:
    def test_registration_needs_two_different_people(self, env, make_user, customer):
        # A03 P2 (M33-1): each step is an M63 inbox decision, never a press on
        # the record, and the administrator round is never routed back to
        # whoever decided the line-manager round.
        lm_grp = "cd_party_master.group_party_registration_lm"
        admin_grp = "cd_party_master.group_party_registration_admin"
        requester = make_user()
        approver = make_user("base.group_partner_manager", lm_grp, admin_grp)
        admin = make_user(admin_grp)
        req = (
            env["fix.registration.approval"]
            .with_user(requester)
            .create({"partner_id": customer.id, "party_class": "dealer"})
        )
        with pytest.raises(UserError, match="inbox"):
            req.action_lm_approve()
        assert requester not in assigned(req)
        approve_via_inbox(req, approver)
        assert assigned(req) == admin
        with pytest.raises(UserError, match="inbox"):
            req.with_user(approver).action_admin_approve()
        with pytest.raises(UserError):
            req.with_user(requester).write({"admin_state": "approved"})

    def test_a_party_is_not_activated_by_editing_its_status(self, env, make_user, customer):
        clerk = make_user("base.group_partner_manager")
        with pytest.raises(UserError):
            customer.with_user(clerk).write({"party_status": "active"})
        # restricting a party stays a plain edit
        customer.with_user(clerk).write({"party_status": "blocked"})
        assert customer.party_status == "blocked"

    def test_reactivation_is_a_tier2_decision(self, env, make_user, customer):
        customer._guarded().write({"party_status": "blocked"})
        with pytest.raises(UserError):
            customer.with_user(make_user("base.group_partner_manager")).action_reactivate_party(
                "please"
            )
        manager = make_user("base.group_partner_manager", T2)
        customer.with_user(manager).action_reactivate_party("Credit cleared by finance.")
        assert customer.party_status == "active"

    def test_a_withdrawn_consent_cannot_be_rewritten_to_granted(self, env, make_user, customer):
        notice = env["fix.transparency.notice"].search([], limit=1) or env[
            "fix.transparency.notice"
        ].create({"version": "BYP-NOTICE-1", "text_en": "n", "text_bn": "n"})
        grant = env["fix.consent"].create(
            {
                "partner_id": customer.id,
                "purpose": "marketing",
                "channel": "sms",
                "state": "granted",
                "proof": "BYP-OTP",
                "notice_version_id": notice.id,
            }
        )
        clerk = make_user()
        grant.with_user(clerk).action_withdraw()
        withdrawal = grant.superseded_by_id
        with pytest.raises(UserError):
            withdrawal.with_user(clerk).write({"state": "granted"})
        with pytest.raises(UserError):
            grant.with_user(clerk).write({"proof": "rewritten"})


# ==========================================================================
# M27 / M32
# ==========================================================================
class TestContactCentre:
    def test_a_conversation_is_not_closed_by_writing_its_state(self, env, make_user, ou):
        agent = make_user()
        conv = (
            env["fix.conversation"]
            .with_user(agent)
            .create({"channel": "chat", "operating_unit_id": ou.id})
        )
        with pytest.raises(UserError):
            conv.write({"state": "resolved_agent"})
        with pytest.raises(UserError):
            conv.write({"recording_sha256": "0" * 64, "recording_consent_state": "granted"})
        conv.action_claim()
        assert conv.state == "with_agent"
        with pytest.raises(ValidationError, match="wrap-up"):
            conv.action_resolve()

    def test_a_suppressed_message_cannot_be_requeued(self, env, make_user, customer):
        delivery = env["fix.notif.delivery"].queue(
            channel="sms", purpose="marketing", partner=customer, body="Promo"
        )
        assert delivery.state == "suppressed"
        with pytest.raises(UserError):
            delivery.with_user(make_user()).write({"state": "queued"})

    def test_a_dataset_is_not_released_by_its_author(self, env, make_user):
        author = make_user(T3)
        ds = (
            env["fix.assistant.dataset"]
            .with_user(author)
            .create({"name": "BYP NLU", "language": "en"})
        )
        with pytest.raises(UserError):
            ds.write({"state": "released"})
        # A03 audit M32 G4: the accuracy is measured, never typed, and the
        # release is decided from the M63 inbox (test_a03_p2_contact_centre).
        with pytest.raises(UserError):
            ds.write({"benchmark_accuracy_pct": 99.0})
        ds._guarded().write({"sha256_checksum": "a" * 64})
        with pytest.raises(UserError, match="inbox"):
            ds.action_release()
        with pytest.raises(UserError, match="inbox"):
            ds.with_user(make_user(T3)).action_release()
        assert ds.state == "draft"


# ==========================================================================
# Discount approval (the quote hand-off from M07)
# ==========================================================================
@pytest.fixture
def estimate_of(env, customer):
    """An estimate prepared by `user`, with a discount of `discount` BDT on 1,000."""

    def _make(user, discount=0.0):
        branch = env["fix.branch"].search([], limit=1)
        if not branch:
            unit = env["operating.unit"].search([], limit=1)
            entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
                {
                    "legal_name": "1000FiX Bypass Probe Ltd",
                    "code": "BYPENT",
                    "company_id": env.company.id,
                    "operating_unit_id": unit.id,
                }
            )
            branch = env["fix.branch"].create(
                {
                    "name": "Bypass Branch",
                    "code": "BYP-BR",
                    "entity_id": entity.id,
                    "operating_unit_id": unit.id,
                }
            )
        brand = env["fix.brand"].create({"name": "BYP Brand", "code": "BYPBR"})
        model = env["fix.device.model"].create({"name": "BYP Model", "brand_id": brand.id})
        device = env["fix.device"].create(
            {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-BYP-1"}
        )
        order = env["fix.service.order"].create(
            {
                "device_id": device.id,
                "customer_id": customer.id,
                "branch_id": branch.id,
                "service_type": "walk_in",
                "order_category": "standard",
                "fault_description": "bypass probe",
            }
        )
        return (
            env["fix.estimate"]
            .with_user(user)
            .create(
                {
                    "order_id": order.id,
                    "discount": discount,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "description": "Part",
                                "line_type": "part",
                                "quantity": 1.0,
                                "unit_price": 1000.0,
                            },
                        )
                    ],
                }
            )
        )

    return _make


class TestDiscountApproval:
    def test_a_requester_cannot_approve_their_own_discount(self, env, make_user, estimate_of):
        requester = make_user()
        estimate = estimate_of(env.user)
        req = (
            env["fix.discount.approval"]
            .with_user(requester)
            .create(
                {
                    "quotation_id": estimate.id,
                    "operating_unit_id": env["operating.unit"].search([], limit=1).id,
                    # A04 build: the single M11 ladder gives the agent 10%.
                    "discount_pct": 15.0,
                    "justification": "Loyal customer",
                }
            )
        )
        assert req.state == "pending"
        with pytest.raises(UserError):
            req.action_approve()  # not from the inbox, and it is their own request
        with pytest.raises(UserError):
            req.write({"state": "approved"})
        manager = make_user(T2)
        req.action_request_approval()
        assert requester not in assigned(req)  # never routed to themselves
        approve_via_inbox(req, manager, requester)
        assert req.state == "approved"

    def test_a_seller_cannot_approve_their_own_estimate_discount(self, env, make_user, estimate_of):
        """A11 P2: the estimate discount DOFA is a routed M63 request — the
        stamp is given from the approver's inbox, never by a direct press."""
        seller = make_user(T4)
        estimate = estimate_of(seller, discount=400.0)  # 40%
        assert estimate.dofa_tier_required == "tier_4"
        with pytest.raises(UserError, match="inbox"):
            estimate.action_dofa_approve()
        with pytest.raises(UserError):
            estimate.write({"dofa_approved_by": seller.id})
        # Routed: the seller asks, is never routed to themselves, and a second
        # Tier-4 holder decides. Asking with no justification is refused at once,
        # not left waiting on a vote that could only refuse.
        director = make_user(T4)  # must exist BEFORE the request routes
        with pytest.raises(UserError, match="justification"), env.cr.savepoint():
            estimate.with_user(seller).action_request_approval()
        assert estimate.approval_state != "pending"
        estimate.with_user(seller).action_request_approval(
            justification="Corporate account retention, signed off by sales head."
        )
        assert seller not in assigned(estimate)  # never routed to themselves
        task = inbox_task(estimate, director)
        assert task, "the Tier-4 director received no inbox task"
        # blanked after the request, the decision still refuses
        estimate.with_user(director).dofa_justification = False
        with pytest.raises(ValidationError, match="justification"), env.cr.savepoint():
            task.with_user(director).action_approve()
        estimate.with_user(
            director
        ).dofa_justification = "Corporate account retention, signed off by sales head."
        task.with_user(director).action_approve()
        assert estimate.dofa_approved_by == director
        assert estimate.dofa_approved_amount == 40.0

    def test_an_estimate_discount_raised_after_approval_needs_reapproval(
        self, env, make_user, estimate_of
    ):
        """R4: the estimate discount runs through fix.dofa.mixin, so the
        amount pin and the immediate withdrawal apply to it as well."""
        seller = make_user()
        estimate = estimate_of(seller, discount=120.0)  # 12% -> Tier 2
        manager = make_user(T2)
        approve_via_inbox(
            estimate, manager, justification="Price match against a competitor quote."
        )
        assert estimate.dofa_approved
        estimate.with_user(seller).write({"discount": 140.0})  # 14%, still Tier 2
        assert not estimate.dofa_approved
        # A02 audit M01-4: only a sent estimate is approvable, so send it; the
        # refusal must then come from the withdrawn DOFA sign-off.
        estimate.with_user(seller).action_send()
        with pytest.raises(ValidationError, match="sign-off"):
            estimate.with_user(seller).action_approve()

    def test_a_front_desk_discount_needs_no_approval(self, env, make_user, estimate_of):
        seller = make_user()
        estimate = estimate_of(seller, discount=40.0)  # 4% -> Tier 1
        assert estimate.dofa_tier_required == "tier_1"
        with pytest.raises(UserError, match="Nothing to approve"):
            estimate.with_user(seller).action_request_approval()
        estimate.with_user(seller)._dofa_assert_approved("Estimate approval")


# ==========================================================================
# A ruling moves the stored tier of records that already exist
# ==========================================================================
def test_putting_a_ladder_in_force_recomputes_existing_tiers(env, make_user, customer, ou):
    c = _complaint(
        env, make_user(), customer, ou, concession_amount=700.0, concession_type="refund"
    )
    assert _stored_tier(env, c) == "tier_1"
    # The module ships the matrix basis for complaints (<= 500 Tier 1,
    # <= 2,500 Tier 2 ...), unruled. Ruling it moves BDT 700 to Tier 2.
    ladder = env["fix.dofa.ladder"].search(
        [("target_model", "=", "fix.complaint"), ("basis", "=", "dofa_matrix")], limit=1
    )
    assert ladder, "the complaint DOFA-matrix ladder is shipped as data"
    expected = next(
        band.tier
        for band in ladder.threshold_ids.sorted("upper_bound")
        if band.upper_bound >= 700.0
    )
    assert expected != "tier_1", "the test needs a ruling that actually changes the tier"
    rule_in_force(env, make_user, ladder, "BYP-RULING-1")
    assert _stored_tier(env, c) == expected


# ==========================================================================
# R2: a posted ledger line is corrected by a reversal, never by an edit
# ==========================================================================
class TestLedgerReversal:
    def _posted(self, env, make_user, account, points):
        line = (
            env["fix.loyalty.ledger"]
            .with_user(make_user())
            .create({"account_id": account.id, "transaction_type": "accrual", "points": points})
        )
        line.action_post()
        return line

    def test_a_small_reversal_posts_and_marks_the_original(self, env, make_user, account):
        line = self._posted(env, make_user, account, 300)
        clerk = make_user()
        with pytest.raises(UserError, match="why"):
            line.with_user(clerk).action_reverse()
        result = line.with_user(clerk).action_reverse(reason="Accrued on a cancelled order")
        reversal = env["fix.loyalty.ledger"].browse(result["reversal_id"])
        assert reversal.points == -300 and reversal.reversal_of_id == line
        assert reversal.transaction_type == "adjustment" and reversal.state == "draft"
        reversal.with_user(clerk).action_post()
        assert line.state == "reversed" and line.points == 300  # history kept as posted
        assert account.points_balance == 0
        with pytest.raises(UserError):
            line.with_user(clerk).action_reverse(reason="again")

    def test_a_large_reversal_needs_a_second_persons_approval(self, env, make_user, account):
        clerk = make_user()
        small = self._posted(env, make_user, account, 400)
        small_rev = env["fix.loyalty.ledger"].browse(
            small.with_user(clerk).action_reverse(reason="Duplicate accrual")["reversal_id"]
        )
        assert small_rev.dofa_tier_required == "tier_0"  # 400 points: below the threshold
        big = self._posted(env, make_user, account, 300)
        # test surgery: make it a large posted credit without a Tier 4 approver
        big._guarded().write({"points": 3000})
        account._guarded().write({"points_balance": 3400})
        big_rev = env["fix.loyalty.ledger"].browse(
            big.with_user(clerk).action_reverse(reason="Mis-keyed accrual")["reversal_id"]
        )
        assert big_rev.dofa_tier_required == "tier_3"
        with pytest.raises(ValidationError):
            big_rev.with_user(clerk).action_post()
        big_rev.with_user(clerk).dofa_justification = "Confirmed mis-key against the source order."
        approve_via_inbox(big_rev, make_user(T3), clerk)
        big_rev.with_user(clerk).action_post()
        assert big.state == "reversed" and account.points_balance == 400

    def test_reversal_fields_cannot_be_forged(self, env, make_user, account):
        line = self._posted(env, make_user, account, 100)
        clerk = make_user()
        draft = (
            env["fix.loyalty.ledger"]
            .with_user(clerk)
            .create({"account_id": account.id, "transaction_type": "adjustment", "points": -100})
        )
        with pytest.raises(UserError):
            draft.write({"reversal_of_id": line.id})


# ==========================================================================
# R5: the hotline hand-off to field dispatch works end to end
# ==========================================================================
@pytest.fixture
def dispatchable(env, customer, ou):
    zone = env["fix.zone"].create({"name": "BYP Dispatch Zone", "code": "BYPDZ"})
    unit = ou
    entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
        {
            "legal_name": "1000FiX Dispatch Probe Ltd",
            "code": "BYPDENT",
            "company_id": env.company.id,
            "operating_unit_id": unit.id,
        }
    )
    branch = env["fix.branch"].create(
        {
            "name": "BYP Dispatch Branch",
            "code": "BYP-DB",
            "entity_id": entity.id,
            "operating_unit_id": unit.id,
            "zone_id": zone.id,
        }
    )
    brand = env["fix.brand"].create({"name": "BYP Disp Brand", "code": "BYPDB"})
    model = env["fix.device.model"].create({"name": "BYP Disp Model", "brand_id": brand.id})
    env["fix.device"].create(
        {
            "device_model_id": model.id,
            "owner_id": customer.id,
            "serial_number": "SN-BYP-DISP",
            "branch_id": branch.id,
        }
    )
    return branch


class TestFieldDispatchHandOff:
    def _conversation(self, env, customer, ou, **vals):
        return env["fix.conversation"].create(
            {
                "channel": "voice",
                "operating_unit_id": ou.id,
                "customer_id": customer.id,
                "intent": "AC not cooling",
                "urgency_level": "critical",
                **vals,
            }
        )

    def test_dispatch_opens_a_service_order_and_a_field_order(
        self, env, customer, ou, dispatchable
    ):
        conv = self._conversation(env, customer, ou)
        conv.action_create_field_work_order()
        fwo = env["fix.field.order"].search([("name", "=", conv.field_work_order_ref)])
        assert fwo, "the hand-off used to raise on a non-existent customer_id"
        assert fwo.zone_id == dispatchable.zone_id and fwo.priority == "3"
        assert fwo.order_id.service_type == "onsite"
        assert fwo.order_id.customer_id == customer
        assert fwo.order_id.priority == "emergency"
        with pytest.raises(UserError, match="already dispatched"):
            conv.action_create_field_work_order()
        with pytest.raises(UserError):
            conv.with_user(env.ref("base.user_admin")).write({"field_work_order_ref": "FAKE"})

    def test_dispatch_without_a_registered_device_is_refused(self, env, ou):
        stranger = env["res.partner"].create({"name": "No Device Customer"})
        conv = self._conversation(env, stranger, ou)
        with pytest.raises(UserError, match="no registered device"):
            conv.action_create_field_work_order()
        assert not conv.field_work_order_ref
