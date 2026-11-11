"""test_a03_p2_crm.py — the A03 P2 repairs to the M07 CRM lifecycle.

Every control is driven as a NON-ADMIN user (a seller, a sales manager, a
DOFA approver), because the superuser is trusted by the field guards and
would hide the gaps the audit found. Each is checked both ways: the bypass
is refused and the legitimate path works.

Findings covered: G-M07-1..11, G-M36-2 (A03 audit, M07_M35.md).
"""

import json
from datetime import timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

REFUSED = (UserError, ValidationError, AccessError)
SELLER = "sales_team.group_sale_salesman_all_leads"
MANAGER = "sales_team.group_sale_manager"
T2 = "cd_entity_config.group_dofa_tier_2"


# --------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------
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
                    "name": "M07 Probe %d" % counter["n"],
                    "login": "m07.p2.probe.%d@crm.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def seller(make_user):
    return make_user(SELLER)


@pytest.fixture
def verifier(make_user):
    return make_user(MANAGER)


@pytest.fixture
def colleague(make_user):
    """A second seller, with exactly a seller's groups. An estimate is never
    approved on its preparer's word alone, and a pre-sales estimate has no
    order and so no customer code to take: a colleague records the approval."""
    return make_user(SELLER)


@pytest.fixture
def corporate(env):
    return env["res.partner"].create({"name": "P2 Corporate Ltd", "is_company": True})


def _opp(env, seller, partner, **vals):
    return (
        env["crm.lead"]
        .with_user(seller)
        .create(
            {
                "name": vals.pop("name", "P2 managed print deal"),
                "type": "opportunity",
                "partner_id": partner.id,
                "user_id": seller.id,
                "expected_revenue": 250000,
                **vals,
            }
        )
    )


def _verify_contract(env, lead, seller, verifier, ref="PO-P2-001"):
    """The routed contract verification: the seller asks, a manager decides."""
    lead.with_user(seller).write({"contract_ref": ref})
    lead.with_user(seller).action_request_contract_verification(justification="PO attached")
    approve_via_inbox(env["crm.lead"].browse(lead.id), verifier, requester=seller)
    lead.invalidate_recordset()
    return lead


def _estimate(env, lead, seller, price=1000.0, discount=0.0):
    """Raise the opportunity's estimate as the seller and price one line."""
    result = lead.with_user(seller).action_raise_estimate()
    estimate = env["fix.estimate"].with_user(seller).browse(result["estimate_id"])
    env["fix.estimate.line"].with_user(seller).create(
        {
            "estimate_id": estimate.id,
            "line_type": "part",
            "description": "Toner kit",
            "quantity": 1,
            "unit_price": price,
        }
    )
    if discount:
        estimate.write({"discount": discount})
    return estimate


# --------------------------------------------------------------------------
# G-M07-3: batch create
# --------------------------------------------------------------------------
def test_batch_create_of_leads_works(env, seller, corporate):
    leads = (
        env["crm.lead"]
        .with_user(seller)
        .create(
            [
                {"name": "Batch lead A", "partner_id": corporate.id},
                {"name": "Batch lead B", "type": "opportunity"},
            ]
        )
    )
    assert len(leads) == 2 and set(leads.mapped("name")) == {"Batch lead A", "Batch lead B"}


# --------------------------------------------------------------------------
# G-M07-1: contract_verified through the M63 engine
# --------------------------------------------------------------------------
def test_seller_cannot_verify_their_own_contract(env, seller, corporate):
    lead = _opp(env, seller, corporate, contract_ref="PO-SELF")
    with pytest.raises(REFUSED):
        lead.with_user(seller).write({"contract_verified": True})
    with pytest.raises(REFUSED):
        lead.with_user(seller).write({"rate_card_approved": True})
    with pytest.raises(REFUSED):
        _opp(env, seller, corporate, name="Born verified", contract_verified=True)
    # Pressing the approve method directly is refused: it is routed.
    with pytest.raises(REFUSED, match="inbox"):
        lead.with_user(seller).action_verify_contract()
    assert not lead.contract_verified


def test_contract_is_verified_by_a_manager_from_the_inbox(env, seller, verifier, corporate):
    lead = _opp(env, seller, corporate)
    with pytest.raises(UserError, match="contract or purchase order reference"):
        lead.with_user(seller).action_request_contract_verification()
    lead.with_user(seller).write({"contract_ref": "PO-P2-777"})
    lead.with_user(seller).action_request_contract_verification(justification="Signed PO")
    lead.invalidate_recordset()
    assert lead.approval_state == "pending"
    assert seller not in assigned(lead), "the seller must never decide their own deal"
    assert verifier in assigned(lead)
    # A manager pressing the method outside the inbox is refused too.
    with pytest.raises(REFUSED, match="inbox"):
        lead.with_user(verifier).action_verify_contract()
    inbox_task(lead, verifier).with_user(verifier).action_approve(comment="PO matches")
    lead.invalidate_recordset()
    assert lead.contract_verified and lead.rate_card_approved
    assert lead.contract_verified_by == verifier
    assert lead.approval_state == "approved"


def test_a_selling_manager_is_not_routed_their_own_deal(env, make_user, verifier, corporate):
    selling_manager = make_user(MANAGER)
    lead = _opp(env, selling_manager, corporate, contract_ref="PO-MGR")
    lead.with_user(selling_manager).action_request_contract_verification()
    lead.invalidate_recordset()
    assert selling_manager not in assigned(lead)
    assert verifier in assigned(lead)


def test_changing_the_contract_reference_withdraws_the_verification(
    env, seller, verifier, corporate
):
    lead = _verify_contract(env, _opp(env, seller, corporate), seller, verifier)
    assert lead.contract_verified
    lead.with_user(seller).write({"contract_ref": "PO-SWAPPED"})
    lead.invalidate_recordset()
    assert not lead.contract_verified and not lead.rate_card_approved
    assert lead.approval_state == "none"


# --------------------------------------------------------------------------
# Item 1 / G-M07-9 / G-M36-2: approved estimate before Won and conversion
# --------------------------------------------------------------------------
def test_won_requires_an_approved_linked_estimate(env, seller, colleague, verifier, corporate):
    lead = _verify_contract(env, _opp(env, seller, corporate), seller, verifier)
    with pytest.raises(ValidationError, match="no estimate"):
        lead.with_user(seller).action_set_won()
    estimate = _estimate(env, lead, seller)
    assert estimate.lead_id == lead and not estimate.order_id
    with pytest.raises(ValidationError, match="must be approved"):
        lead.with_user(seller).action_set_won()
    estimate.with_user(seller).action_send()  # A02 M01-4: only a sent estimate is approved
    estimate.with_user(colleague).action_approve()
    assert estimate.state == "approved" and estimate.approval_stamped_at
    assert estimate.approved_total == estimate.grand_total
    lead.with_user(seller).action_set_won()
    assert lead.won_status == "won"
    assert lead.quote_status.startswith("Approved")


def test_a_seller_cannot_approve_the_presales_estimate_they_prepared(
    env, seller, colleague, verifier, corporate
):
    """Segregation of duties on the pre-sales path. A CRM estimate has no
    order, so there is no customer code to take: the seller who prepared it is
    refused, and it is a colleague's approval that lets the deal be won."""
    lead = _verify_contract(env, _opp(env, seller, corporate), seller, verifier)
    estimate = _estimate(env, lead, seller)
    assert estimate.create_uid == seller and not estimate.order_id
    estimate.with_user(seller).action_send()
    with pytest.raises(UserError, match="Segregation of duties: you prepared estimate"):
        estimate.with_user(seller).action_approve()
    estimate.invalidate_recordset()
    assert estimate.state == "sent" and not estimate.approval_stamped_at
    # no order means no customer to send an approval code to
    with pytest.raises(UserError, match="no valid Bangladesh mobile number"):
        estimate.with_user(seller).action_send_customer_otp()
    assert not estimate.customer_approval_ref
    with pytest.raises(ValidationError, match="must be approved"):
        lead.with_user(seller).action_set_won()
    assert lead.won_status != "won"
    # the legitimate path: a colleague, holding only a seller's groups, approves
    estimate.with_user(colleague).action_approve()
    assert estimate.state == "approved" and estimate.approval_stamped_at
    assert estimate.approved_total == estimate.grand_total
    lead.with_user(seller).action_set_won()
    assert lead.won_status == "won"


def test_creating_a_deal_already_won_is_refused(env, seller, corporate):
    with pytest.raises(ValidationError, match="created already won|REQ-07.1"):
        _opp(env, seller, corporate, name="Instant win", probability=100)


def test_linked_estimate_cannot_be_forced_to_approved(env, seller, corporate):
    lead = _opp(env, seller, corporate)
    estimate = _estimate(env, lead, seller)
    with pytest.raises(UserError, match="Approve action"):
        estimate.with_user(seller).write({"state": "approved"})
    with pytest.raises(REFUSED):
        estimate.with_user(seller).write({"approval_stamped_at": fields.Datetime.now()})
    assert estimate.state == "draft"


def test_an_edit_after_approval_blocks_the_win(env, seller, colleague, verifier, corporate):
    lead = _verify_contract(env, _opp(env, seller, corporate), seller, verifier)
    estimate = _estimate(env, lead, seller)
    estimate.with_user(seller).action_send()  # A02 M01-4: only a sent estimate is approved
    estimate.with_user(colleague).action_approve()
    # A02 M01-5: the approved estimate's lines are now frozen outright
    with pytest.raises(UserError, match="frozen"):
        env["fix.estimate.line"].with_user(seller).create(
            {"estimate_id": estimate.id, "description": "Extra drum", "unit_price": 900.0}
        )
    # The legitimate path: revise, approve the revision, win.
    revision = estimate.with_user(seller).action_revise()
    revised = env["fix.estimate"].browse(revision["res_id"])
    assert revised.lead_id == lead and revised.state == "draft"
    revised.with_user(seller).action_send()
    revised.with_user(colleague).action_approve()
    lead.with_user(seller).action_set_won()
    assert lead.won_status == "won"


def test_pending_discount_approval_is_voided_by_an_edit(
    env, seller, colleague, verifier, make_user, corporate
):
    """The engine's void-on-change limits edits while approval is pending."""
    approver = make_user(T2)
    lead = _verify_contract(env, _opp(env, seller, corporate), seller, verifier)
    estimate = _estimate(env, lead, seller, price=4000.0, discount=400.0)  # 10%: Tier 2
    estimate.with_user(seller).action_send()  # A02 M01-4: only a sent estimate is approved
    estimate.with_user(seller).action_request_approval(justification="Strategic account")
    estimate.invalidate_recordset()
    assert estimate.approval_state == "pending"
    with pytest.raises(ValidationError, match="must be approved"):
        lead.with_user(seller).action_set_won()
    # Raising the discount while the request is pending voids it.
    estimate.with_user(seller).write({"discount": 600.0})
    estimate.invalidate_recordset()
    assert estimate.approval_state == "none"
    with pytest.raises(REFUSED):
        estimate.with_user(colleague).action_approve()  # DOFA sign-off missing
    # Re-request, the Tier 2 approver decides it, then the estimate approves.
    approve_via_inbox(
        env["fix.estimate"].browse(estimate.id),
        approver,
        requester=seller,
        justification="Strategic account",
    )
    estimate.invalidate_recordset()
    assert estimate.dofa_approved and estimate.dofa_approved_by == approver
    estimate.with_user(colleague).action_approve()
    lead.with_user(seller).action_set_won()
    assert lead.won_status == "won"


def test_a_rejected_discount_request_blocks_the_win(env, seller, colleague, verifier, corporate):
    if "fix.discount.approval" not in env:
        pytest.skip("cd_quotation is not installed")
    lead = _verify_contract(env, _opp(env, seller, corporate), seller, verifier)
    estimate = _estimate(env, lead, seller)
    estimate.with_user(seller).action_send()  # A02 M01-4: only a sent estimate is approved
    estimate.with_user(colleague).action_approve()
    request = env["fix.discount.approval"].create(
        {
            "quotation_id": estimate.id,
            "operating_unit_id": env["operating.unit"].search([], limit=1).id,
            "discount_pct": 40.0,
            "justification": "Competitive tender",
        }
    )
    request._approval_on_rejected("Too deep")
    assert request.state == "rejected"
    with pytest.raises(ValidationError, match="rejected"):
        lead.with_user(seller).action_set_won()


def test_estimate_links_once(env, seller, corporate):
    first = _opp(env, seller, corporate, name="First deal")
    second = _opp(env, seller, corporate, name="Second deal")
    estimate = _estimate(env, first, seller)
    with pytest.raises(UserError, match="already quotes"):
        second.with_user(seller).action_link_estimate(estimate=str(estimate.id))
    with pytest.raises(UserError, match="number of an existing estimate"):
        second.with_user(seller).action_link_estimate(estimate="none")
    assert first.with_user(seller).action_link_estimate(estimate="#%d" % estimate.id)["note"]


# --------------------------------------------------------------------------
# Conversion: estimate moves onto the order; B2B gets a clear refusal
# --------------------------------------------------------------------------
@pytest.fixture
def device_for(env):
    def _make(partner):
        company = env["res.company"].create({"name": "P2 Conversion Co"})
        entity = env["fix.entity"].create(
            {"code": "P2ENT", "legal_name": "P2 Entity", "company_id": company.id}
        )
        branch = env["fix.branch"].create(
            {
                "name": "P2 Motijheel",
                "code": "P2MJ",
                "entity_id": entity.id,
                "operating_unit_id": env["operating.unit"].search([], limit=1).id,
            }
        )
        brand = env["fix.brand"].create({"name": "P2Brand", "code": "P2BR"})
        model = env["fix.device.model"].create({"name": "P2 Printer", "brand_id": brand.id})
        return env["fix.device"].create(
            {
                "device_model_id": model.id,
                "owner_id": partner.id,
                "serial_number": "SN-P2-001",
                "branch_id": branch.id,
            }
        )

    return _make


def test_b2b_without_a_device_gets_a_contract_path(env, seller, colleague, verifier, corporate):
    lead = _verify_contract(env, _opp(env, seller, corporate), seller, verifier)
    b2b_estimate = _estimate(env, lead, seller)
    b2b_estimate.with_user(seller).action_send()  # A02 M01-4: only a sent estimate is approved
    b2b_estimate.with_user(colleague).action_approve()
    lead.with_user(seller).action_set_won()
    with pytest.raises(ValidationError, match="corporate account .* M08"):
        lead.with_user(seller).action_convert_to_service_order()
    assert not lead.converted_service_order_id


def test_conversion_carries_the_approved_estimate(
    env, seller, colleague, verifier, corporate, device_for
):
    device_for(corporate)
    lead = _verify_contract(env, _opp(env, seller, corporate), seller, verifier)
    estimate = _estimate(env, lead, seller)
    estimate.with_user(seller).action_send()  # A02 M01-4: only a sent estimate is approved
    estimate.with_user(colleague).action_approve()
    lead.with_user(seller).action_set_won()
    lead.with_user(seller).action_convert_to_service_order()
    order = lead.converted_service_order_id
    assert order and estimate.order_id == order
    with pytest.raises(UserError, match="already converted"):
        lead.with_user(seller).action_convert_to_service_order()
    with pytest.raises(REFUSED):
        lead.with_user(seller).write({"converted_service_order_id": False})


# --------------------------------------------------------------------------
# G-M07-2: loss analysis cannot be skipped by archiving
# --------------------------------------------------------------------------
def test_archiving_an_open_deal_requires_the_loss_analysis(env, seller, corporate):
    lead = _opp(env, seller, corporate, probability=60)
    with pytest.raises(ValidationError, match="Loss analysis"):
        lead.with_user(seller).action_archive()
    lead.with_user(seller).write({"probability": 0.5})
    with pytest.raises(ValidationError, match="Loss analysis"):
        lead.with_user(seller).write({"active": False})
    # The P03 Mark Lost path: competitor on the form, reason in the prompt.
    lead.with_user(seller).write({"competitor": "RivalFix"})
    lead.with_user(seller).action_set_lost(reason="PRICE")
    assert not lead.active and lead.lost_reason_code == "PRICE" and lead.probability == 0


def test_plain_leads_archive_freely(env, seller):
    lead = env["crm.lead"].with_user(seller).create({"name": "Spam enquiry", "type": "lead"})
    lead.with_user(seller).action_archive()
    assert not lead.active


# --------------------------------------------------------------------------
# G-M07-11: shipped stage gates apply to leads with no pipeline
# --------------------------------------------------------------------------
def test_standard_stage_gates_ship_and_apply(env, seller, corporate):
    pipeline = env.ref("cd_crm_ext.pipeline_standard")
    rules = pipeline.stage_rules()
    assert rules["Qualified"]["requires_confirmation"]
    assert rules["Proposition"]["requires_confirmation"]
    qualified = env["crm.stage"].search([("name", "=", "Qualified")], limit=1)
    if not qualified:
        pytest.skip("no 'Qualified' crm.stage in this database")
    lead = _opp(env, seller, corporate)
    assert not lead.pipeline_id
    with pytest.raises(ValidationError, match="BRU-CRM-03"):
        lead.with_user(seller).write({"stage_id": qualified.id})
    lead.with_user(seller).write({"stage_id": qualified.id, "criteria_confirmed": True})
    assert lead.stage_id == qualified and not lead.criteria_confirmed


def test_migration_fills_only_pipelines_without_rules(env):
    bare = env["fix.pipeline"].create({"code": "P2-BARE", "name": "Bare", "revenue_stream": "msp"})
    custom = env["fix.pipeline"].create(
        {
            "code": "P2-CUSTOM",
            "name": "Custom",
            "revenue_stream": "amc",
            "stages_json": json.dumps([{"stage": "Discovery", "requires_confirmation": True}]),
        }
    )
    env["fix.pipeline"]._apply_default_stage_gates()
    assert "Qualified" in bare.stage_rules()
    assert list(custom.stage_rules()) == ["Discovery"]


# --------------------------------------------------------------------------
# G-M07-4 / G-M07-8: routing, scheduling, and the rescore cron
# --------------------------------------------------------------------------
def test_route_by_score_finds_the_default_cadence(env, seller, corporate):
    cadence = env["fix.crm.sequence"].create(
        {
            "name": "P2 hot-lead cadence",
            "code": "P2-HOT",
            "step_ids": [(0, 0, {"name": "Call", "step_type": "call", "instructions": "Call."})],
        }
    )
    cadence.action_activate()
    lead = _opp(env, seller, corporate)
    lead.sudo().write({"lead_score_band": "hot"})
    result = lead.with_user(seller).action_route_by_score()
    assert result["routed"] == 1


def test_account_management_crons_are_scheduled(env):
    for xmlid, code in (
        ("cd_crm_ext.ir_cron_qbr_at_risk", "model.cron_flag_qbr_at_risk()"),
        ("cd_crm_ext.ir_cron_forecast_snapshot", "model.action_take_snapshot()"),
        ("cd_crm_ext.ir_cron_renewal_creation", "model.cron_create_renewals()"),
        ("cd_crm_ext.ir_cron_lead_rescore", "model.cron_rescore_open_leads()"),
    ):
        cron = env.ref(xmlid)
        assert cron.active and cron.code.strip() == code
        model, method = cron.model_id.model, code.split(".")[1].split("(")[0]
        assert callable(getattr(env[model], method, None)), "%s has no %s" % (model, method)


def test_scheduled_methods_do_their_work(env, seller, corporate):
    account = env["fix.account"].create({"partner_id": corporate.id, "tier": "strategic"})
    assert env["fix.account"].cron_flag_qbr_at_risk() >= 1
    assert account.health_rating == "at_risk"
    pipeline = env.ref("cd_crm_ext.pipeline_standard")
    _opp(
        env, seller, corporate, pipeline_id=pipeline.id, forecast_category="commit", probability=40
    )
    env["fix.forecast.snapshot"].action_take_snapshot(period="2099-01")
    snap = env["fix.forecast.snapshot"].search(
        [("period", "=", "2099-01"), ("owner_id", "=", seller.id)]
    )
    assert snap.commit_value == 250000
    if "fix.contract" in env:
        assert isinstance(env["fix.renewal"].cron_create_renewals(), int)


def test_rescore_cron_survives_a_failing_lead(env, seller, corporate):
    good = _opp(env, seller, corporate, name="Scores fine")
    bad = _opp(env, seller, corporate, name="Breaks scoring")
    Model = type(env["fix.crm.score.model"])
    original = Model.score

    def flaky(self, lead):
        if lead.id == bad.id:
            raise RuntimeError("engine fault")
        return original(self, lead)

    with mock.patch.object(Model, "score", flaky):
        result = env["crm.lead"].cron_rescore_open_leads()
    assert result["failed"] >= 1 and result["scored"] >= 1
    assert good.lead_scored_at and not bad.lead_scored_at


# --------------------------------------------------------------------------
# G-M07-7 / G-M07-10: renewal buttons that exist, outcomes that are guarded
# --------------------------------------------------------------------------
def test_renewal_engage_renew_and_lapse_once(env, seller, corporate):
    Renewal = env["fix.renewal"].with_user(seller)
    renewal = Renewal.create(
        {"source_type": "contract", "partner_id": corporate.id, "expiry_date": fields.Date.today()}
    )
    with pytest.raises(REFUSED):
        renewal.write({"state": "renewed"})
    renewal.action_engage()
    assert renewal.state == "engaged" and renewal.engaged_at and renewal.owner_id == seller
    renewal.action_renew()
    assert renewal.state == "renewed"
    with pytest.raises(UserError, match="only an open renewal"):
        renewal.action_lapse()

    lapsing = Renewal.create(
        {"source_type": "contract", "partner_id": corporate.id, "expiry_date": fields.Date.today()}
    )
    lapsing.action_lapse()
    assert lapsing.state == "lapsed" and lapsing.winback_lead_id
    with pytest.raises(UserError, match="only an open renewal"):
        lapsing.action_lapse()
    closing = Renewal.create(
        {"source_type": "contract", "partner_id": corporate.id, "expiry_date": fields.Date.today()}
    )
    with pytest.raises(UserError, match="why"):
        closing.action_close()
    closing.action_close(reason="Customer closed the site")
    assert closing.state == "closed"


def test_auto_created_flag_cannot_be_cleared_to_delete(env, seller, corporate):
    renewal = env["fix.renewal"].create(
        {
            "source_type": "contract",
            "partner_id": corporate.id,
            "expiry_date": fields.Date.today(),
            "auto_created": True,
        }
    )
    with pytest.raises(REFUSED):
        renewal.with_user(seller).write({"auto_created": False})


# --------------------------------------------------------------------------
# G-M07-5 / G-M07-6: cadence
# --------------------------------------------------------------------------
def _cadence(env, *steps):
    seq = env["fix.crm.sequence"].create(
        {
            "name": "P2 cadence",
            "code": "P2-CAD-%d" % len(steps),
            "step_ids": [(0, 0, dict(step, sequence=10 * (i + 1))) for i, step in enumerate(steps)],
        }
    )
    seq.action_activate()
    return seq


def _advance(seq, enrolment):
    enrolment.sudo().write({"next_action_at": fields.Datetime.now() - timedelta(minutes=1)})
    seq._runtime_advance_due()
    enrolment.invalidate_recordset()


def test_waiting_manual_step_does_not_trip_the_loop_guard(env, seller, corporate):
    seq = _cadence(env, {"name": "Call", "step_type": "call", "instructions": "Call them."})
    lead = _opp(env, seller, corporate)
    enrolment = seq.enrol(lead)
    _advance(seq, enrolment)
    assert enrolment.steps_executed == 1  # the activity was raised
    for _ in range(4):
        _advance(seq, enrolment)
    assert enrolment.steps_executed == 1 and enrolment.manual_rechecks == 4
    # Even right at the guard, a seller's inaction is not a runaway flow.
    enrolment.sudo().write({"steps_executed": 499})
    for _ in range(3):
        _advance(seq, enrolment)
    assert enrolment.state == "active" and enrolment.steps_executed == 499


def test_cold_prospect_email_needs_marketing_consent(env, seller):
    prospect = env["res.partner"].create({"name": "Cold Prospect", "email": "cold@p2.test"})
    seq = _cadence(env, {"name": "Intro", "step_type": "email", "email_body": "Hello"})
    lead = (
        env["crm.lead"]
        .with_user(seller)
        .create({"name": "Cold lead", "partner_id": prospect.id, "email_from": "cold@p2.test"})
    )
    enrolment = seq.enrol(lead)
    _advance(seq, enrolment)
    delivery = enrolment.delivery_ids
    assert delivery.lawful_basis == "consent" and delivery.purpose == "marketing"
    assert delivery.state == "suppressed"
    assert not enrolment.first_touch_at, "a suppressed e-mail is not a touch"


def test_customer_under_contract_is_emailed_under_the_contract_basis(
    env, seller, verifier, corporate
):
    corporate.email = "it@p2corp.test"
    seq = _cadence(env, {"name": "Kick-off", "step_type": "email", "email_body": "Welcome"})
    lead = _verify_contract(env, _opp(env, seller, corporate), seller, verifier)
    enrolment = seq.enrol(lead)
    _advance(seq, enrolment)
    assert enrolment.delivery_ids.lawful_basis == "contract"


# --------------------------------------------------------------------------
# R8: journey.lead_requested
# --------------------------------------------------------------------------
def _relay(env):
    env.flush_all()
    env["fix.event.outbox"].cron_relay(limit=5000)


def test_journey_lead_request_creates_one_lead_and_links_repeats(env, corporate, seller):
    consumer = env.ref("cd_crm_ext.consumer_journey_lead_requested")
    consumer.active_from = fields.Datetime.now() - timedelta(days=1)
    env.cr.execute("UPDATE fix_event_outbox SET relayed_at = now() WHERE relayed_at IS NULL")
    env["fix.account.assignment"].create(
        {"partner_id": corporate.id, "owner_id": seller.id, "assignment_type": "account"}
    )
    payload = {
        "journey_id": 9101,
        "journey": "P2 nurture",
        "campaign_id": 77,
        "partner_id": corporate.id,
        "step": "Hand to sales",
        "note": "Clicked the AMC offer twice",
    }
    publish(env, "journey.lead_requested", "fix.campaign.journey.member", 1, payload)
    _relay(env)
    Lead = env["crm.lead"].with_context(active_test=False)
    leads = Lead.search([("source_ref", "=", "journey:9101:partner:%d" % corporate.id)])
    assert len(leads) == 1
    lead = leads
    assert lead.lead_source == "campaign" and lead.user_id == seller and lead.source_event_id
    # The same event again (a redelivery) is a no-op.
    event = env["fix.event.outbox"].search([("event_id", "=", lead.source_event_id)])
    assert Lead.consume_journey_lead_requested(event._relay_event_dict()) == lead
    # A second request for the same party by the same journey links, not duplicates.
    publish(env, "journey.lead_requested", "fix.campaign.journey.member", 2, payload)
    _relay(env)
    assert Lead.search_count([("source_ref", "=", lead.source_ref)]) == 1
    assert len((lead.source_event_log or "").split()) == 1


def test_journey_lead_without_a_party_is_still_raised(env):
    event = {
        "event_id": "p2-anon-0001",
        "aggregate_id": 55,
        "payload": {"journey_id": 9102, "journey": "Anon", "partner_id": False, "note": ""},
        "company_id": env.company.id,
    }
    lead = env["crm.lead"].consume_journey_lead_requested(event)
    assert lead.source_ref == "journey:9102:member:55" and not lead.partner_id
    assert env["crm.lead"].consume_journey_lead_requested(event) == lead


# --------------------------------------------------------------------------
# P03: every M07 button is whitelisted
# --------------------------------------------------------------------------
def test_every_m07_button_is_whitelisted():
    import re
    from pathlib import Path

    # Merged across areas: M07-quotes uses the fix.estimate surface of M01.
    from odoo.addons.cd_p03_portal.controllers.p03_generic_api import SURFACES

    js = (
        Path(__file__).resolve().parents[4] / "platform/cd_p03_portal/static/src/a03/m07.js"
    ).read_text(encoding="utf-8")
    screens = re.split(r"\n  '(M07-[a-z0-9-]+)': \{", js)
    missing = []
    for sid, body in zip(screens[1::2], screens[2::2], strict=True):
        model = re.search(r"model: '([a-z0-9_.]+)'", body)
        if not model:
            continue
        for method in re.findall(r"\{ m: '([a-z_]+)'", body):
            if method not in SURFACES.get(model.group(1), {}).get("actions", set()):
                missing.append("%s %s.%s" % (sid, model.group(1), method))
    assert not missing, missing


def test_assigning_unowned_accounts_is_a_managers_call(env, seller, verifier):
    env["res.partner"].create({"name": "P2 Unowned Customer", "customer_rank": 1})
    with pytest.raises(UserError, match="sales manager"):
        env["fix.account.assignment"].with_user(seller).action_assign_unowned()
    assert env["fix.account.assignment"].with_user(verifier).action_assign_unowned() >= 1
