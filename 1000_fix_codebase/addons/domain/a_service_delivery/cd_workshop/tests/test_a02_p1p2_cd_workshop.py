"""A02 workflow audit, P1/P2 for M31 Workshop & Depot Repair.

B1 (routed approvals: BER write-off, extra parts, certification waiver), B2
(BER and delivery reach M01) and the M31 lifecycle repairs (book-in, the
estimate link and re-approval, the parts cap, real stock moves, BER evidence,
the comeback link, receiving from M01). Every control is tested both ways as
NON-ADMIN users from the A02 M31 fixture (test_a02_p0_m31.py) or created
here; `odoo_env` rolls everything back.
"""

import json

from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, inbox_task
from odoo.exceptions import UserError

from . import test_a02_p0_m31 as a02

m31 = a02.m31
refused, _as, _user = a02.refused, a02._as, a02._user
_evidence, _to_repair, _approved_estimate = a02._evidence, a02._to_repair, a02._approved_estimate
_set_order_state, _line = a02._set_order_state, a02._line


def _tier2(m, tag="t2", extra=()):
    env = m.env
    return _user(env, tag, [env.ref("cd_entity_config.group_dofa_tier_2"), *extra])[0]


def _events(env, rec, event_type):
    rows = (
        env["fix.event.outbox"]
        .sudo()
        .search([("aggregate_id", "=", rec.id), ("event_type", "=", event_type)])
    )
    out = []
    for row in rows:
        data = json.loads(row.payload or "{}")
        out.append(data.get("payload", data) if isinstance(data, dict) else data)
    return out


# --- book-in (M31 step 2) -------------------------------------------------------


def test_intake_needs_the_book_in_and_freezes_it(m31):
    job = m31.job(bookin_condition=False, bookin_no_accessories=False)
    with refused(m31.env, UserError, "condition at book-in"):
        job.action_intake()
    job.write({"bookin_condition": "Cracked bezel, top-left"})
    with refused(m31.env, UserError, "accessories received"):
        job.action_intake()
    job.write({"bookin_accessories": "Charger, USB-C cable"})
    job.action_intake()
    assert (job.state, job.bookin_by_id) == ("intake", m31.tech) and job.bookin_at
    with refused(m31.env, UserError, "book-in is the receipt"):
        job.write({"bookin_accessories": "nothing"})
    with refused(m31.env, UserError, "changes only through its workflow"):
        job.write({"bookin_by_id": m31.tech2.id})
    assert "bookin_condition" in job._fix_form_locked_fields()


def test_the_book_in_is_copied_from_the_m01_intake(m31):
    so = m31.order(state="intake")
    so.sudo().write(
        {"cosmetic_condition_notes": "Dent on the back", "accessory_bag_barcode": "BAG-77"}
    )
    job = so.with_user(m31.tech).action_create_workshop_job()
    assert job.bookin_condition == "Dent on the back"
    assert job.bookin_accessory_bag == "BAG-77" and "BAG-77" in job.bookin_accessories
    job.with_user(m31.tech).action_intake()
    assert job.state == "intake"


# --- receive from M01 (M31 step 1) --------------------------------------------------


def test_a_draft_order_is_not_received_and_the_workshop_receives_by_reference(m31):
    draft = m31.order(state="draft")
    with refused(m31.env, UserError, "still a draft"):
        draft.action_create_workshop_job()
    so = m31.order(state="intake")
    with refused(m31.env, UserError, "Workshop role"):
        m31.workshop.with_user(m31.plain).action_receive_service_order(so.name)
    with refused(m31.env, UserError, "was not found"):
        m31.workshop.with_user(m31.tech).action_receive_service_order("SO/NOPE/1")
    res = m31.workshop.with_user(m31.tech).action_receive_service_order(so.name)
    job = m31.env["fix.workshop.job"].browse(res["job_id"])
    assert (job.order_id, job.workshop_id, job.state) == (so, m31.workshop, "draft")


# --- the estimate and the parts cap (M31 step 5-6, BRU-WSR-11) ---------------------


def test_the_cap_is_the_latest_approved_version_and_counts_labour(m31):
    so = m31.order()
    _approved_estimate(m31, so, 30000.0)
    v2 = _approved_estimate(m31, so, 10000.0)
    v2.sudo().write({"version": 2})
    job = _to_repair(m31, m31.job(so=so))
    assert (job.estimate_id, job.estimate_ceiling) == (v2, v2.approved_total or v2.grand_total)
    ceiling = job.estimate_ceiling
    # P0 summed v1 + v2: a 25,000 part fitted under a 10,000 approval
    with refused(m31.env, UserError, "BRU-WSR-11"):
        _line(m31, job, cost=ceiling + 1).action_consume_part()
    job.write({"labour_total": ceiling - 1000.0})
    with refused(m31.env, UserError, "BRU-WSR-11"):
        _line(m31, job, cost=2000.0).action_consume_part()
    small = _line(m31, job, cost=900.0)
    small.action_consume_part()
    assert small.reservation_state == "consumed" and not job.cost_over_estimate


def test_cost_rising_after_approval_stops_qc_until_re_approved(m31):
    so = m31.order()
    _approved_estimate(m31, so, 5000.0)
    job = _to_repair(m31, m31.job(so=so))
    _line(m31, job, cost=4000.0).action_consume_part()
    job.write({"labour_total": 3000.0})
    job.invalidate_recordset()
    assert job.cost_over_estimate
    with refused(m31.env, UserError, "rose after approval"):
        job.action_submit_qc()
    # the customer re-approves a revised estimate (v2): the job goes on
    v2 = _approved_estimate(m31, so, 9000.0)
    v2.sudo().write({"version": 2})
    job.action_submit_qc()
    assert job.state == "qc_pending"


def test_a_zero_charge_order_is_held_to_the_cap(m31):
    so = m31.order()  # approved on an entitlement: no estimate
    job = _to_repair(m31, m31.job(so=so))
    with refused(m31.env, UserError, "BRU-WSR-11"):
        _line(m31, job, cost=500.0).action_consume_part()
    m31.env["ir.config_parameter"].sudo().set_param("cd_workshop.zero_charge_parts_cap_bdt", "800")
    _line(m31, job, cost=500.0).action_consume_part()
    with refused(m31.env, UserError, "BRU-WSR-11"):
        _line(m31, job, cost=500.0).action_consume_part()


def test_an_extra_part_is_fitted_after_a_routed_approval(m31):
    env = m31.env
    so = m31.order()
    _approved_estimate(m31, so, 1000.0)
    job = _to_repair(m31, m31.job(so=so))
    extra = _line(m31, job, cost=6000.0)
    with refused(env, UserError, "Request Approval"):
        extra.action_consume_part()
    approver = _tier2(m31, "xp")  # a DOFA Tier 2 holder with NO workshop role
    # nobody approves by pressing the button, not even the tier holder
    with refused(env, UserError, "approver's inbox"):
        extra.with_user(approver).action_dofa_approve()
    extra.action_request_approval(justification="Customer agreed by phone; logged")
    assert extra.approval_state == "pending" and extra._dofa_current_tier() == "tier_2"
    # the technician who added the part is never routed it
    assert not inbox_task(extra, m31.tech)
    approve_via_inbox(extra, approver)
    extra.invalidate_recordset()
    assert (extra.dofa_approved, extra.dofa_approved_by) == (True, approver)
    extra.action_consume_part()
    assert extra.reservation_state == "consumed"
    # an approved extra part stands outside the estimate: the job goes to QC
    job.action_submit_qc()
    assert job.state == "qc_pending"


def test_an_extra_part_approval_does_not_cover_a_raised_quantity(m31):
    so = m31.order()
    _approved_estimate(m31, so, 1000.0)
    job = _to_repair(m31, m31.job(so=so))
    extra = _line(m31, job, cost=3000.0)
    approve_via_inbox(extra, _tier2(m31, "xq"), justification="needed")
    extra.write({"quantity": 3.0})  # BDT 9,000 now
    extra.invalidate_recordset()
    assert not extra.dofa_approved
    with refused(m31.env, UserError, "Request Approval"):
        extra.action_consume_part()


# --- real stock (M31 step 6) ----------------------------------------------------------


def _store(m, qty):
    env = m.env
    parent = env.ref("stock.stock_location_stock")
    loc = env["stock.location"].create(
        {"name": "A02 bench store %s" % m.workshop.code, "location_id": parent.id}
    )
    m.workshop.write({"stock_location_id": loc.id})
    product = env["product.product"].create(
        {"name": "A02 stocked part", "default_code": "A02-STK-%s" % m.workshop.code,
         "type": "consu", "is_storable": True, "standard_price": 100.0}
    )  # fmt: skip
    if qty:
        env["stock.quant"]._update_available_quantity(product, loc, qty)
    return loc, product


def test_parts_are_reserved_and_consumed_as_stock_moves(m31):
    env = m31.env
    loc, product = _store(m31, 1.0)
    so = m31.order()
    _approved_estimate(m31, so)
    job = _to_repair(m31, m31.job(so=so))
    Line = env["fix.workshop.part.line"].with_user(m31.tech)
    two = Line.create({"job_id": job.id, "product_id": product.id, "quantity": 2.0})
    with refused(env, UserError, "cannot be reserved"):
        two.action_reserve()
    one = Line.create({"job_id": job.id, "product_id": product.id, "quantity": 1.0})
    one.action_reserve()
    move = one.sudo().stock_move_id
    assert (one.reservation_state, move.state, move.location_id) == ("reserved", "assigned", loc)
    one.action_consume_part()
    assert move.state == "done" and one.consumption_ref == (move.reference or "MOVE/%d" % move.id)
    assert env["stock.quant"]._get_available_quantity(product, loc) == 0.0
    # the move is written by the consumption only
    with refused(env, UserError, "changes only through its workflow"):
        two.write({"stock_move_id": move.id})


def test_a_released_reservation_cancels_its_move(m31):
    _loc, product = _store(m31, 3.0)
    so = m31.order()
    _approved_estimate(m31, so)
    job = _to_repair(m31, m31.job(so=so))
    line = (
        m31.env["fix.workshop.part.line"]
        .with_user(m31.tech)
        .create({"job_id": job.id, "product_id": product.id, "quantity": 1.0})
    )
    line.action_reserve()
    line.action_release_reservation()
    assert (line.reservation_state, line.sudo().stock_move_id.state) == ("released", "cancel")


def test_the_stock_switch_refuses_a_workshop_without_a_store(m31):
    so = m31.order()
    _approved_estimate(m31, so)
    job = _to_repair(m31, m31.job(so=so))
    line = _line(m31, job)
    m31.env["ir.config_parameter"].sudo().set_param("cd_workshop.stock_moves_required", "1")
    with refused(m31.env, UserError, "no parts store location"):
        line.action_reserve()


# --- BER / scrap (B1, B2, M31 steps 11-12) ----------------------------------------------


def _ber_ready(m, so_state="in_repair"):
    so = m.order(state=so_state)
    job = m.job(so=so)
    job.action_intake()
    job.action_diagnostic()
    return so, job


def test_a_ber_needs_evidence(m31):
    _so, job = _ber_ready(m31, "diagnostic")
    with refused(m31.env, UserError, "needs its evidence"):
        job.action_propose_ber("Liquid damage", writeoff_amount=500.0)
    _evidence(m31, job, "pre_repair_photo")
    job.action_propose_ber("Liquid damage", writeoff_amount=500.0)
    assert job.ber_proposed_at


def test_an_approved_ber_closes_the_job_and_the_order(m31):
    so, job = _ber_ready(m31, "diagnostic")
    _evidence(m31, job, "diagnostic_report")
    job.action_propose_ber("PMIC shorted, board cracked", writeoff_amount=4000.0)
    job.sudo().write({"dofa_justification": "Photos and the diagnostic report attached"})
    approver = _tier2(m31, "ber")  # no workshop role: the apply runs under his ACLs
    _as(m31, m31.tech2, job).action_confirm_ber()
    assert job.sudo().approval_state == "pending" and job.sudo().state == "diagnostic"
    # neither the confirmer nor the repairing technician is routed it
    assert not inbox_task(job.sudo(), m31.tech2) and not inbox_task(job.sudo(), m31.tech)
    approve_via_inbox(job.sudo(), approver, requester=m31.tech2)
    job.invalidate_recordset()
    assert (job.state, job.approval_state, job.dofa_approved_by) == (
        "unrepairable",
        "approved",
        approver,
    )
    assert (so.state, so.cancel_reason_code) == ("cancelled", "unrepairable")


def test_a_ber_is_refused_where_m01_cannot_follow(m31):
    so, job = _ber_ready(m31, "diagnostic")
    _evidence(m31, job, "diagnostic_report")
    job.action_propose_ber("Board cracked", writeoff_amount=4000.0)
    _set_order_state(so, "qc_pending")
    with refused(m31.env, UserError, "cannot close as BER while its service order"):
        _as(m31, m31.tech2, job).action_confirm_ber()


def test_a_rejected_ber_needs_a_new_confirmation(m31):
    _so, job = _ber_ready(m31, "diagnostic")
    _evidence(m31, job, "diagnostic_report")
    job.action_propose_ber("Board cracked", writeoff_amount=4000.0)
    job.sudo().write({"dofa_justification": "see report"})
    approver = _tier2(m31, "rej")
    _as(m31, m31.tech2, job).action_confirm_ber()
    task = inbox_task(job.sudo(), approver)
    task.with_user(approver).action_reject(comment="Try the donor board first")
    job.invalidate_recordset()
    assert (job.state, job.approval_state, job.ber_confirmed_at) == (
        "diagnostic",
        "rejected",
        False,
    )
    with refused(m31.env, UserError, "no confirmed BER"):
        job.action_request_approval()


# --- the certification waiver, routed (B1) ------------------------------------------------


def test_the_waiver_is_granted_from_a_supervisors_inbox_only(m31):
    env = m31.env
    job = m31.job(level="l2")
    job.action_intake()
    job.action_request_certification_waiver("M22 course booked for next week")
    req = env["fix.workshop.waiver.request"].search([("job_id", "=", job.id)])
    with refused(env, UserError, "already has a waiver"):
        job.action_request_certification_waiver("again")
    # a direct grant is refused, even for a supervisor
    with refused(env, UserError, "approver's inbox"):
        req.with_user(m31.supv).action_grant()
    with refused(env, UserError, "changes only through its workflow"):
        req.with_user(m31.supv).write({"state": "granted"})
    # a supervisor who is the repairing technician is never routed it
    supv2, supv2_emp = _user(env, "supv2", [env.ref("cd_workshop.group_fix_workshop_manager")])
    job2 = m31.job(level="l2", technician_id=supv2_emp.id)
    job2.action_request_certification_waiver("cover for leave")
    req2 = env["fix.workshop.waiver.request"].search([("job_id", "=", job2.id)])
    assert supv2 not in req2.approval_request_id.task_ids.mapped("assigned_user_id")
    approve_via_inbox(req, m31.supv)
    job.invalidate_recordset()
    assert (job.certification_waiver, job.certification_waiver_by_id, req.state) == (
        True,
        m31.supv,
        "granted",
    )
    assert job._m31_waiver_covers(m31.tech_emp) and not job._m31_waiver_covers(m31.tech2_emp)


# --- delivered event, comeback (B2) --------------------------------------------------------


def test_delivery_publishes_the_m01_hand_back(m31):
    so = m31.order()
    est = _approved_estimate(m31, so, 3000.0)
    job = a02._qc_ready(m31, m31.job(so=so))
    _as(m31, m31.qc, job).action_pass_qc()
    a02._handover_ready(m31, so)
    so.sudo().write(
        {"payment_settlement_state": "settled", "amount_settled_bdt": est.grand_total,
         "settlement_verified": True}
    )  # fmt: skip
    job.action_deliver()
    payloads = _events(m31.env, job, "workshop.job.delivered")
    assert len(payloads) == 1
    assert (payloads[0]["service_order_id"], payloads[0]["workshop_job_id"]) == (so.id, job.id)


def test_a_comeback_is_linked_to_the_prior_repair(m31):
    original = m31.order()
    prior = m31.job(so=original)
    prior.sudo()._guarded().write({"state": "delivered"})
    comeback = m31.order(state="intake")
    comeback.sudo()._guarded().write({"is_rework": True, "rework_of_id": original.id})
    job = comeback.with_user(m31.tech).action_create_workshop_job()
    assert (job.rework_of_id, job.is_comeback, job.comeback_technician_id) == (
        prior,
        True,
        m31.tech_emp,
    )
    with refused(m31.env, UserError, "changes only through its workflow"):
        job.write({"rework_of_id": False})


# --- the workspace ----------------------------------------------------------------------------


def test_the_workspace_routes_approvals_instead_of_pressing_them():
    from odoo.addons.cd_p03_portal.controllers.a02 import m31 as surface

    job_actions = surface.SURFACES["fix.workshop.job"]["actions"]
    assert "action_dofa_approve" not in job_actions
    assert {"action_request_certification_waiver", "action_confirm_ber"} <= job_actions
    assert "action_receive_service_order" in surface.SURFACES["fix.workshop"]["actions"]
    assert "action_request_approval" in surface.SURFACES["fix.workshop.part.line"]["actions"]
    assert "action_dofa_approve" not in surface.SURFACES["fix.workshop.part.line"]["actions"]
