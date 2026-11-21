# M14 second capture pass (19 Nov 2026): each sub-module page captures what
# the spec (FR-TRF-001..039, §9 rules, §13 SoD) says it captures.
#
# Before: the intake had no channel or declaration and the post-inspection
# value was typed with no evidence; a valuation had no economics; payouts were
# always mobile money; no rework, no ownership proof for an activation-lock
# removal; the grade was a free choice; QA kept two counters; listing never
# re-checked NEIR; nothing captured a return or a parts-only write-off.
#
# Run as NON-ADMIN users (the `m` fixture), through the real /p03/model/write
# and /p03/model/action endpoints where the workspace uses them; the odoo_env
# fixture rolls everything back.
# ruff: noqa: F811 - `m` is the shared M14 fixture, taken as each test's argument
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_tradein.tests.test_a05_m14_controls import (  # noqa: F401 - m is a fixture
    GUARD,
    TRD,
    accepted,
    approved,
    certify,
    finish_steps,
    graded,
    intake_at_offer,
    intake_verified,
    m,
    p03_action,
    p03_write,
    paying,
    priced,
    qa,
    refurbishing,
    refused,
    request,
    resale,
    routed_to_parts,
    screen,
)
from odoo.exceptions import UserError, ValidationError

TIC = "fix.tradein.intake.check"
RRT = "fix.refurb.return"
RWO = "fix.refurb.writeoff"


def _photo(x, name="evidence.jpg"):
    return x.env["ir.attachment"].create({"name": name, "raw": b"jpg"})


# ======================================================== p1 intake: channel + declaration
def test_intake_captures_channel_declaration_and_accessories_from_the_form(m):
    partner = m.env["res.partner"].create({"name": "A05 M14 Portal Seller"})
    res = p03_write(
        m,
        TRD,
        None,
        {
            "customer_id": partner.id,
            "operating_unit_id": m.ou.id,
            "intake_channel": "portal",
            "declared_condition": "good",
            "declared_faults": "Face ID intermittent",
            "declared_age_months": 18,
            "oem_warranty_status": "expired",
            "acc_charger": True,
            "acc_box": True,
        },
    )
    assert "error" not in res, res
    rec = m.env[TRD].browse(res["id"])
    assert (rec.intake_channel, rec.declared_condition, rec.declared_age_months) == (
        "portal",
        "good",
        18,
    )
    assert rec.acc_charger and rec.acc_box and not rec.acc_cable


def test_the_declaration_freezes_once_the_offer_is_sent(m):
    rec = request(m, declared_condition="good", intake_channel="counter")
    from odoo.addons.cd_tradein.tests.test_a05_m14_controls import valued

    valued(m, rec)
    rec.action_send_offer()
    refused(lambda: rec.write({"declared_condition": "as_new"}), "frozen")
    assert p03_write(m, TRD, rec.id, {"acc_charger": True}).get("error")
    screen(m, rec)
    rec.action_accept()
    refused(lambda: rec.write({"intake_channel": "app"}), "frozen")


def test_a_corporate_lot_opens_corporate_channel_intakes(m):
    client = m.env["res.partner"].create({"name": "A05 M14 Fleet Client", "is_company": True})
    lot = (
        m.env["fix.bulk.buyback"]
        .with_user(m.clerk)
        .create(
            {
                "partner_id": client.id,
                "operating_unit_id": m.ou.id,
                "asset_ids": [(0, 0, {"serial_number": "A05M14-FLEET-1"})],
            }
        )
    )
    lot.action_open_intakes()
    assert lot.asset_ids.tradein_id.intake_channel == "corporate"


# ======================================================== p1 BRU-TRF-09 intake verification
def test_a_lower_value_is_refused_without_a_verified_photographed_difference(m):
    rec = paying(m, request(m, declared_condition="good"))
    refused(lambda: rec.write({"graded_value": 15000}), GUARD)
    res = p03_write(m, TRD, rec.id, {"graded_value": 15000})
    assert res.get("error"), res
    Check = m.env[TIC].with_user(m.clerk2)
    # not worse than declared: the offer stands
    same = Check.create(
        {"tradein_id": rec.id, "verified_condition": "good", "verified_value": 15000}
    )
    refused(same.action_confirm, "offer stands")
    # worse, but no description / no photographs
    worse = Check.create(
        {"tradein_id": rec.id, "verified_condition": "poor", "verified_value": 15000}
    )
    assert worse.condition_differs
    refused(worse.action_confirm, "describe")
    worse.write({"difference_notes": "Cracked back glass"})
    refused(worse.action_confirm, "photographs")
    # an intake check never raises the offer
    up = Check.create({"tradein_id": rec.id, "verified_condition": "good", "verified_value": 25000})
    refused(up.action_confirm, "does not raise")
    # the valuer does not confirm the condition (§13)
    worse.write({"evidence_attachment_id": _photo(m).id})
    refused(lambda: worse.with_user(m.clerk).action_confirm(), "Segregation")
    res = p03_action(m, TIC, worse, "action_confirm", user=m.clerk2)
    assert res["success"], res
    assert worse.state == "confirmed" and worse.checked_by_id == m.clerk2
    assert rec.graded_value == 15000 and rec.revision_state == "pending"
    refused(lambda: worse.write({"verified_value": 1.0}), "can no longer change")
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        worse.write({"state": "draft"})


def test_the_unit_received_must_be_the_one_offered(m):
    rec = accepted(m)
    row = (
        m.env[TIC]
        .with_user(m.clerk2)
        .create(
            {
                "tradein_id": rec.id,
                "verified_condition": "good",
                "identity_matches": False,
                "verified_value": 20000,
            }
        )
    )
    refused(row.action_confirm, "not the one the offer was made on")


def test_no_intake_check_once_a_payout_is_in_approval(m):
    rec = paying(m)
    approved(m, rec)
    refused(
        lambda: m.env[TIC]
        .with_user(m.clerk2)
        .create({"tradein_id": rec.id, "verified_condition": "poor", "verified_value": 100}),
        "before its payout is requested",
    )
    draft = request(m)
    refused(
        lambda: m.env[TIC]
        .with_user(m.clerk2)
        .create({"tradein_id": draft.id, "verified_condition": "poor", "verified_value": 100}),
        "after acceptance",
    )


# ======================================================== p2 offer economics
def test_an_offer_is_built_from_its_economics(m):
    rec = request(m)
    Val = m.env["fix.tradein.valuation"].with_user(m.clerk)
    bare = Val.create({"tradein_id": rec.id})
    refused(bare.action_apply_to_tradein, "FR-TRF-033")
    thin = Val.create(
        {
            "tradein_id": rec.id,
            "resale_estimate": 24000,
            "expected_refurb_cost": 1500,
            "expected_logistics_cost": 300,
            "expected_destruction_cost": 200,
            "expected_channel_cost": 1000,
        }
    )
    assert thin.computed_offer == 20000
    assert thin.expected_cost_total == 3000 and thin.modelled_margin == 1000
    assert thin.modelled_margin_pct == pytest.approx(4.17, abs=0.01)
    assert thin.margin_floor_pct == 15.0 and thin.below_margin_floor and thin.is_override
    refused(thin.action_apply_to_tradein, "state its reason")
    thin.write({"override_reason": "Flagship model, fast seller"})
    thin.action_request_override_approval()
    refused(lambda: thin.write({"resale_estimate": 90000}), "frozen")
    thin.with_user(m.valmgr).action_approve_override()
    thin.action_apply_to_tradein()
    assert rec.offered_value == 20000


# ======================================================== p4 settlement method
def test_settlement_method_is_pinned_and_reaches_treasury(m):
    rec = paying(m)
    intake_at_offer(m, rec)
    rec.write({"settlement_method": "bank_transfer"})
    refused(rec.action_request_payout_approval, "bank account")
    stranger = m.env["res.partner"].create({"name": "A05 M14 Stranger"})
    Bank = m.env["res.partner.bank"].sudo()
    foreign = Bank.create({"acc_number": "A05M14-0001", "partner_id": stranger.id})
    rec.write({"settlement_bank_account_id": foreign.id})
    refused(rec.action_request_payout_approval, "not the seller")
    own = Bank.create({"acc_number": "A05M14-0002", "partner_id": rec.customer_id.id})
    rec.write({"settlement_bank_account_id": own.id})
    approved(m, rec)
    rec.write({"settlement_method": "cash"})  # the approval covered a bank transfer
    assert rec.payout_approval_state == "none"
    rec.write({"settlement_method": "bank_transfer"})
    approved(m, rec)
    rec.action_pay()
    pay = rec.payout_execution_id.sudo()
    assert pay.method == "bank_transfer" and pay.partner_bank_id == own


# ======================================================== p7 rework + ownership proof
def test_a_step_after_a_failed_qa_is_rework_with_its_cause_and_cost(m):
    rec = refurbishing(m)
    finish_steps(m, rec, parts=100.0, labour=100.0)
    qa(m, rec, passed=10, total=12)  # fails at the 100% default
    Step = m.env["fix.refurbishment"].with_user(m.tech)
    refused(lambda: Step.create({"tradein_id": rec.id, "step": "repair"}), "FR-TRF-036")
    step = Step.create(
        {"tradein_id": rec.id, "step": "repair", "rework_cause": "missed_fault", "labor_cost": 400}
    )
    assert step.is_rework and step.rework_qa_id.qa_state == "fail"
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        step.write({"is_rework": False})
    assert rec.rework_cost == 400
    assert rec.first_pass_cost == sum(rec.refurbishment_ids.mapped("total_cost")) - 400


def test_activation_lock_removal_needs_proof_of_ownership(m):
    rec = refurbishing(m)
    step = rec.refurbishment_ids.filtered(lambda s: s.step == "repair")
    with pytest.raises(ValidationError, match="BRU-TRF-22"), m.env.cr.savepoint():
        step.with_user(m.tech).write({"activation_lock_removed": True})
    step.with_user(m.tech).write(
        {"activation_lock_removed": True, "ownership_proof_id": _photo(m, "receipt.pdf").id}
    )
    assert step.activation_lock_removed


# ======================================================== p8 computed grade + override
def _qa_ready(x, battery=100):
    rec = refurbishing(x)
    finish_steps(x, rec)
    qa(x, rec, battery=battery)  # A05 ERP M14-14: the battery is the QA's
    return rec


def test_the_grade_is_computed_from_the_axes_and_the_battery(m):
    rec = _qa_ready(m, battery=78)
    Grade = m.env["fix.tradein.grade"].with_user(m.clerk)
    refused(
        lambda: Grade.create({"tradein_id": rec.id, "screen_grade": "b", "battery_health_pct": 90}),
        "measurement",
    )
    row = Grade.create({"tradein_id": rec.id, "screen_grade": "b"})
    # worst axis B; 78% is below B's 80% minimum, above C's 75%: C
    assert row.computed_grade == "c" and row.grade == "c" and not row.is_override
    assert row.qa_id and row.battery_minimum_pct == 75
    # BRU-TRF-14: no override lifts a battery below the grade minimum
    refused(
        lambda: Grade.with_user(m.supervisor).create(
            {"tradein_id": rec.id, "grade": "a", "override_reason": "x"}
        ),
        "BRU-TRF-14",
    )


def test_a_grade_override_is_justified_by_a_supervisor_who_did_not_run_the_qa(m):
    rec = _qa_ready(m)
    Grade = m.env["fix.tradein.grade"]
    vals = {"tradein_id": rec.id, "cosmetic_grade": "c", "grade": "b"}
    refused(lambda: Grade.with_user(m.supervisor).create(dict(vals)), "justification")
    vals["override_reason"] = "Scuff is on the removable case only"
    refused(lambda: Grade.with_user(m.clerk).create(dict(vals)), "Refurbishment Supervisor")
    m.qa.write({"group_ids": [(4, m.env.ref("cd_tradein.group_refurb_supervisor").id)]})
    refused(lambda: Grade.with_user(m.qa).create(dict(vals)), "T-07")
    row = Grade.with_user(m.supervisor).create(dict(vals))
    assert row.is_override and row.computed_grade == "c" and row.grade == "b"
    assert row.override_by_id == m.supervisor and row.override_at
    with pytest.raises(UserError, match=GUARD), m.env.cr.savepoint():
        row.with_user(m.supervisor).write({"override_by_id": m.clerk.id})


def test_grading_takes_the_certificate_never_a_typed_grade(m):
    rec = _qa_ready(m)
    refused(rec.action_grade, "grading certificate")
    # the state gate holds it too, for any path that is not the action
    assert "no grading certificate" in rec._tradein_gate_denial("graded")
    certify(m, rec, "c")
    rec.write({"grade": "a"})  # typed on the request: not what was measured
    res = p03_action(m, TRD, rec, "action_grade")
    assert res["success"], res
    assert rec.state == "graded" and rec.grade == "c" and rec.refurb_grade_id.code == "C"


def test_qa_totals_come_from_the_recorded_tests(m):
    rec = refurbishing(m)
    finish_steps(m, rec)
    row = (
        m.env["fix.refurb.qa"]
        .with_user(m.clerk)
        .create(
            {
                "tradein_id": rec.id,
                "tests_total": 12,
                "tests_passed": 12,
                "test_ids": [
                    (0, 0, {"test_code": "display", "outcome": "pass"}),
                    (0, 0, {"test_code": "camera", "outcome": "pass"}),
                    (0, 0, {"test_code": "battery", "measured": "71%", "outcome": "fail"}),
                ],
            }
        )
    )
    row.with_user(m.qa).action_submit_result()
    assert (row.tests_total, row.tests_passed, row.qa_state) == (3, 2, "fail")
    test = row.test_ids[0]
    refused(lambda: test.with_user(m.clerk).write({"outcome": "fail"}), "frozen")
    refused(
        lambda: m.env["fix.refurb.qa.test"]
        .with_user(m.clerk)
        .create({"qa_id": row.id, "test_code": "ports"}),
        "frozen",
    )


# ======================================================== p9 NEIR at listing + returns
def test_listing_a_handset_re_confirms_its_neir_screen(m):
    rec = paying(m)
    approved(m, rec)
    rec.action_pay()  # A05 ERP D3: on the ledger before it is listed
    graded(m, rec)
    priced(m, rec)
    prov = rec.provenance_ids
    prov.sudo().write({"checked_on": fields.Date.today() - timedelta(days=40)})
    refused(rec.action_resale_ready, "NEIR")
    screen(m, rec)
    rec.action_resale_ready()
    assert rec.state == "resale_ready"


def _sold(x):
    # A05 ERP D3: the seller is paid at purchase; the sale then takes the unit
    # off the refurbished-stock ledger
    rec = paying(x)
    approved(x, rec)
    rec.action_pay()
    resale(x, rec)
    stock = rec.graded_stock_id
    stock.sudo().action_sell()
    x.env[TRD].sudo().consume_graded_stock_sold(
        {"aggregate": "fix.graded.stock", "aggregate_id": stock.id, "payload": {}}
    )
    return rec


def test_a_return_is_only_of_a_sold_unit_within_its_terms(m):
    unsold = resale(m)
    refused(
        lambda: m.env[RRT].with_user(m.clerk).create({"tradein_id": unsold.id, "reason": "doa"}),
        "only a sold",
    )
    rec = _sold(m)
    late = (
        m.env[RRT]
        .with_user(m.clerk)
        .create(
            {
                "tradein_id": rec.id,
                "reason": "hardware",
                "failure_code": "BOARD-01",
                "return_date": fields.Date.today() + timedelta(days=4000),
            }
        )
    )
    refused(late.action_receive, "outside its return window")


def test_a_return_records_the_failure_and_a_supervisor_decides(m):
    rec = _sold(m)
    res = p03_write(m, RRT, None, {"tradein_id": rec.id, "reason": "battery"})
    assert "error" not in res, res
    ret = m.env[RRT].browse(res["id"]).with_user(m.clerk)
    assert ret.grade_at_sale == "b" and ret.warranty_id.state == "active"
    refused(ret.action_receive, "failure code")
    ret.write({"failure_code": "BAT-SWELL"})
    res = p03_action(m, RRT, ret, "action_receive")
    assert res["success"], res
    assert ret.state == "received" and ret.within_terms
    assert ret.warranty_id.claims_count == 1
    refused(lambda: ret.write({"failure_code": "X"}), "can no longer change")
    ret.write({"outcome": "re_refurbish"})
    refused(ret.action_decide, "Refurbishment Supervisor")
    # the person who received it does not decide it, even as a supervisor
    m.clerk.write({"group_ids": [(4, m.env.ref("cd_tradein.group_refurb_supervisor").id)]})
    refused(ret.action_decide, "received the return")
    res = p03_action(m, RRT, ret, "action_decide", user=m.supervisor)
    assert res["success"], res
    assert ret.state == "decided" and ret.decided_by_id == m.supervisor


# ======================================================== p10 parts-only routing + write-off
def test_parts_only_routing_needs_two_signatures_before_any_harvest(m):
    unit = graded(m, grade="e")
    line = (
        m.env["fix.tradein.harvest"]
        .with_user(m.clerk)
        .create({"tradein_id": unit.id, "component": "battery", "target": "recycle"})
    )
    refused(line.action_harvest, "parts only")
    row = (
        m.env[RWO]
        .with_user(m.clerk)
        .create({"tradein_id": unit.id, "cause": "qa_failed", "destination": "recycle"})
    )
    refused(row.action_request, "Refurbishment Supervisor")
    row = row.with_user(m.supervisor)
    refused(row.action_request, "why the unit cannot be sold")
    row.write({"cause_notes": "Display and board both failed QA"})
    res = p03_action(m, RWO, row, "action_request", user=m.supervisor)
    assert res["success"], res
    assert row.state == "pending" and row.accumulated_cost == unit.inventory_valuation
    refused(lambda: row.write({"destination": "harvest"}), "can no longer change")
    m.supervisor.write({"group_ids": [(4, m.env.ref(GROUP_WO).id)]})
    refused(row.action_approve, "Segregation")
    refused(lambda: row.with_user(m.clerk).action_approve(), "Write-off Approver")
    res = p03_action(m, RWO, row, "action_approve", user=m.woapprover)
    assert res["success"], res
    assert row.state == "approved" and row.approved_by_id == m.woapprover
    # A05 ERP M14-09: the approval routes the unit to parts only
    assert unit.state == "parts_only" and unit.written_off
    # the routing gate is passed: a recycle line needs no receiving bin
    line.action_harvest()
    assert line.state == "harvested"


GROUP_WO = "cd_tradein.group_refurb_writeoff_approver"


def test_cost_to_complete_routing_must_exceed_the_resale_estimate(m):
    rec = refurbishing(m)
    row = (
        m.env[RWO]
        .with_user(m.supervisor)
        .create(
            {
                "tradein_id": rec.id,
                "cause": "cost_to_complete",
                "cause_notes": "Needs a new board",
                "resale_estimate": 9000,
                "cost_to_complete": 5000,
            }
        )
    )
    refused(row.action_request, "above the resale estimate")
    row.write({"cost_to_complete": 12000})
    row.action_request()
    assert row.state == "pending"
    second = (
        m.env[RWO]
        .with_user(m.supervisor)
        .create({"tradein_id": rec.id, "cause": "other", "cause_notes": "dup"})
    )
    refused(second.action_request, "already has")
    assert routed_to_parts  # the shared helper drives the approved routing elsewhere
