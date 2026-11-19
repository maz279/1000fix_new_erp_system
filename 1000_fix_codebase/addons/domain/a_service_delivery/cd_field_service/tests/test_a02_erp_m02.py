"""A02 ERP audit (19 Nov 2026), M02 Field Service & Dispatch: the findings as
executable controls, each tested both ways as non-admin users.

  F1/F20  field cash: the technician declares, a cashier of the service
          order's branch accepts it into that branch's open drawer, with a
          movement reference; the order's settlement is verified as the cashier
  F3      geofence / zone / service order frozen once dispatched; an arrival
          with no fence needs a dispatcher's waiver
  F4      the van follows the technician on dispatch and reassignment
  F10     a reassignment is a logged dispatch decision
  F11     the optimised stop order is kept; the route's own depot is used
  F13     field cash still held from earlier days is outstanding
  F14     on-site payment and van stock reports read the field order's own data
  F18     a field order from a service order is not scheduled at its SLA deadline
  F21     KPI row: drafts are not "unassigned", unscheduled arrivals are not late

``odoo_env`` rolls back after every test.
"""

import json
import types
from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.addons.cd_competency.tests.certify import certify_for_dispatch, licence_for_driving
from odoo.addons.cd_field_service.tests import test_a02_p0_m02 as p0

# the P0 world (company, branch, zone, technicians A and B, a dispatcher)
w = p0.w
_fence, _open_shift, give_evidence, p03, refused = (
    p0._fence,
    p0._open_shift,
    p0.give_evidence,
    p0.p03,
    p0.refused,
)


# ------------------------------------------------------------------ helpers
def _user(w, login, *groups):
    env = w.env
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "company_id": w.co.id,
                "company_ids": [(6, 0, [w.co.id])],
                "operating_unit_ids": [(6, 0, w.ou.ids)],
                "default_operating_unit_id": w.ou.id,
            }
        )
    )
    env["hr.employee"].create({"name": login, "user_id": user.id})
    return user


def _walk(rec, user):
    """Accept, travel, arrive inside the zone fence, start work."""
    if not rec._fix_arrival_fences():
        _fence(_w_of(rec))
    r = rec.with_user(user)
    r.action_accept()
    r.action_start_travel()
    r.action_arrive(position="23.8, 90.4")
    r.action_start_work()


def _w_of(rec):
    return types.SimpleNamespace(env=rec.env, zone=rec.zone_id)


def _completed_cash(w, so, amount=3000):
    rec = w.fo("dispatched", w.ea, order_id=so.id)
    _walk(rec, w.ua)
    rec.with_user(w.ua).action_record_collection(payment="cash %s" % amount)
    give_evidence(rec)
    rec.with_user(w.ua).action_complete()
    assert rec.onsite_payment_state == "pending_handover"
    return rec


CASHIER_GROUPS = ("cd_service_order.group_so_cashier", "cd_front_desk.group_fd_cashier")


# ======================================================= F1/F20 field cash
def test_field_cash_is_declared_then_accepted_by_a_cashier_of_the_branch(w, monkeypatch):
    so = w.so()
    rec = _completed_cash(w, so)
    shift = _open_shift(w)
    cashier = _user(w, "erp_m02_cashier", *CASHIER_GROUPS)

    # step 1: the technician declares - no drawer movement, settlement unverified
    rec.with_user(w.ua).action_handover_field_cash()
    assert rec.onsite_payment_state == "pending_acceptance"
    assert (rec.cash_declared_by_id, rec.cash_shift_id) == (w.ua, rec.cash_shift_id.browse())
    assert not shift.field_cash_deposited
    assert (so.payment_settlement_state, so.settlement_verified) == ("settled", False)
    assert so.invoice_ref == "COD/%s" % rec.name
    if "settlement_tender" in so._fields:
        assert so.settlement_tender == "cash"
    # declared once
    assert refused(w.env, lambda: rec.with_user(w.ua).action_handover_field_cash())

    # neither the technician, a plain dispatcher nor another technician accepts
    # (the field order's own check refuses them: the M01 verification behind it
    # must not be the only gate)
    for user, why in ((w.ua, "cashier or branch manager"), (w.ud, "cashier or branch manager"),
                      (w.ub, "cashier or branch manager")):  # fmt: skip
        err = refused(w.env, lambda user=user: rec.with_user(user).action_accept_field_cash())
        assert err and why in err, (user.login, err)
    # a technician who is also a cashier still cannot accept the cash they collected
    w.ua.sudo().write({"group_ids": [(4, w.env.ref(g).id) for g in CASHIER_GROUPS]})
    err = refused(w.env, lambda: rec.with_user(w.ua).action_accept_field_cash())
    assert err and "technician who collected" in err
    assert not shift.field_cash_deposited and rec.onsite_payment_state == "pending_acceptance"

    # step 2: the branch cashier, through the workspace
    _mw, ma = p03(w, cashier, monkeypatch)
    res = ma(model="fix.field.order", ids=[rec.id], method="action_accept_field_cash")
    w.env.invalidate_all()
    assert res.get("success"), res
    assert shift.field_cash_deposited == 3000.0
    assert (rec.cash_shift_id, rec.cash_accepted_by_id) == (shift, cashier)
    assert rec.cash_handed_over_at and rec.onsite_payment_state == "settled"
    assert so.settlement_verified and so.settlement_verified_by == cashier
    movement = w.env["fix.cash.movement"].search([("shift_id", "=", shift.id)])
    assert movement.reference == "Field cash %s / %s" % (rec.name, so.name)
    # accepted once
    assert refused(w.env, lambda: rec.with_user(cashier).action_accept_field_cash())
    assert shift.field_cash_deposited == 3000.0


def test_the_declarer_cannot_accept_their_own_declaration(w):
    so = w.so()
    rec = _completed_cash(w, so, 900)
    _open_shift(w)
    disp_cashier = _user(
        w, "erp_m02_dispcash", "cd_field_service.group_fix_field_service_manager", *CASHIER_GROUPS
    )
    rec.with_user(disp_cashier).action_handover_field_cash()  # a dispatcher declares for the tech
    err = refused(w.env, lambda: rec.with_user(disp_cashier).action_accept_field_cash())
    assert err and "whoever declared it handed over" in err
    other = _user(w, "erp_m02_cashier2", *CASHIER_GROUPS)
    rec.with_user(other).action_accept_field_cash()
    assert rec.onsite_payment_state == "settled"


def test_cash_goes_only_to_the_service_order_branch_shift(w):
    so = w.so()
    rec = _completed_cash(w, so, 1200)
    cashier = _user(w, "erp_m02_cashier3", *CASHIER_GROUPS)
    rec.with_user(w.ua).action_handover_field_cash()
    # another branch of the same company has a newer open shift
    other_branch = w.env["fix.branch"].create(
        {
            "name": "ERP M02 Other Branch",
            "code": "EM2OB",
            "entity_id": w.branch.entity_id.id,
            "operating_unit_id": w.ou.id,
        }
    )
    foreign = (
        w.env["fix.cash.shift"]
        .sudo()
        .create(
            {
                "branch_id": other_branch.id,
                "operating_unit_id": w.ou.id,
                "operator_id": w.ed.id,
                "opening_float": 100.0,
                "company_id": w.co.id,
            }
        )
    )
    # no open shift at the order's branch: refused, the other branch's is not taken
    err = refused(w.env, lambda: rec.with_user(cashier).action_accept_field_cash())
    assert err and "no open cash shift" in err and not foreign.field_cash_deposited
    own = _open_shift(w)
    # naming the other branch's shift is refused
    err = refused(w.env, lambda: rec.with_user(cashier).action_accept_field_cash(foreign.id))
    assert err and "not that branch's" in err
    rec.with_user(cashier).action_accept_field_cash()
    assert (own.field_cash_deposited, foreign.field_cash_deposited) == (1200.0, 0.0)


def test_mfs_collection_tells_the_order_its_tender(w):
    so = w.so()
    seen = []

    def stub(self, amount, ref, source=None):
        seen.append((self.env.context.get("fd_settlement_tender"), amount, ref, source))

    with patch.object(type(so), "_fix_record_settlement", new=stub, create=True):
        rec = w.fo("dispatched", w.ea, order_id=so.id)
        _walk(rec, w.ua)
        rec.with_user(w.ua).action_record_collection(payment="nagad 700 TRX-NG-1")
        give_evidence(rec)
        rec.with_user(w.ua).action_complete()
    assert seen == [("nagad", 700.0, "TRX-NG-1", "field_collection")]


# ================================================= F13 cash reconciliation
def test_cash_recon_counts_cash_still_held_from_earlier_days(w):
    so = w.so()
    old = _completed_cash(w, so, 500)
    yesterday = fields.Datetime.now() - timedelta(days=1)
    old.sudo()._guarded().write({"completed_at": yesterday})
    so2 = w.so()
    new = _completed_cash(w, so2, 800)
    Recon = w.env["fix.field.cash.recon"]
    rec = Recon.with_user(w.ua).create({"employee_id": w.ea.id})
    assert (rec.order_count, rec.cash_collected, rec.cash_outstanding) == (1, 800.0, 1300.0)
    assert old.name in rec.order_refs and new.name in rec.order_refs
    # a declared but not accepted hand-over is still outstanding
    old.with_user(w.ua).action_handover_field_cash()
    assert rec._fix_measure()["cash_outstanding"] == 1300.0
    # accepted into a drawer: no longer with the technician
    _open_shift(w)
    old.with_user(_user(w, "erp_m02_cashier4", *CASHIER_GROUPS)).action_accept_field_cash()
    figures = rec._fix_measure()
    assert (figures["cash_outstanding"], figures["cash_handed_over"]) == (800.0, 500.0)


# =========================================================== F3 site freeze
def test_site_fields_freeze_once_dispatched(w, monkeypatch):
    other_so = w.so()
    fence = _fence(w)
    draft = w.fo("draft")
    draft.with_user(w.ud).write({"geofence_id": fence.id})  # before dispatch: the form
    assert draft.geofence_id == fence
    rec = w.fo("dispatched", w.ea, geofence_id=fence.id)
    far = _fence(w, lat=24.5, lng=91.0)
    for vals in ({"geofence_id": far.id}, {"geofence_id": False}, {"order_id": other_so.id}):
        for user in (w.ua, w.ud):
            err = refused(w.env, lambda vals=vals, user=user: rec.with_user(user).write(vals))
            assert err and "in dispatch" in err, vals
    mw, _ma = p03(w, w.ua, monkeypatch)
    res = mw(model="fix.field.order", record_id=rec.id, values={"geofence_id": far.id})
    w.env.invalidate_all()
    assert res.get("error") and rec.geofence_id == fence
    assert {"geofence_id", "zone_id", "order_id"} <= rec._fix_form_locked_fields()
    # the dispatcher's action, with a reason
    assert refused(w.env, lambda: rec.with_user(w.ua).action_set_geofence(change="%d x" % far.id))
    assert "reason" in refused(w.env, lambda: rec.with_user(w.ud).action_set_geofence(far.id))
    rec.with_user(w.ud).action_set_geofence(change="%d Customer moved" % far.id)
    assert rec.geofence_id == far and rec.order_id == w.order


def test_arrival_with_no_fence_needs_a_dispatcher_waiver_in_strict_mode(w):
    w.env["ir.config_parameter"].sudo().set_param("cd_field_service.arrival_requires_fence", "1")
    rec = w.fo("en_route", w.ea)
    assert not rec._fix_arrival_fences()
    err = refused(w.env, lambda: rec.with_user(w.ua).action_arrive(position="23.8, 90.4"))
    assert err and "no geofence" in err and rec.state == "en_route"
    rec.with_user(w.ud).action_waive_geofence("Zone fences not drawn yet")
    rec.with_user(w.ua).action_arrive(position="23.8, 90.4")
    assert rec.state == "arrived"


def test_a_fenceless_arrival_records_its_position_by_default(w):
    """Owner decision 20 Nov 2026: until fences are drawn, a fenceless order
    checks in on its GPS position, which is recorded as the proof."""
    w.env["ir.config_parameter"].sudo().set_param("cd_field_service.arrival_requires_fence", "0")
    rec = w.fo("en_route", w.ea)
    assert not rec._fix_arrival_fences()
    err = refused(w.env, lambda: rec.with_user(w.ua).action_arrive())
    assert err and "current position" in err and rec.state == "en_route"
    rec.with_user(w.ua).action_arrive(position="23.8, 90.4")
    assert rec.state == "arrived"
    assert (round(rec.arrival_latitude, 1), round(rec.arrival_longitude, 1)) == (23.8, 90.4)


# =========================================================== F4 van stock
def _van(w, emp, code):
    licence_for_driving(w.env, emp)  # FR-HSE-019: van work needs a licence
    return w.env["fix.stock.location"].create(
        {"name": "Van %s" % code, "code": code, "location_type": "van", "technician_id": emp.id}
    )


def test_the_van_follows_the_technician(w):
    van_a, van_b = _van(w, w.ea, "EM2VA"), _van(w, w.eb, "EM2VB")
    rec = w.fo("pending_dispatch")
    rec.with_user(w.ud).action_dispatch(technician_id=w.ea.id)
    assert rec.van_location_id == van_a
    product = w.env["product.product"].create({"name": "ERP M02 relay"})
    line = w.env["fix.field.order.part"].create(
        {"field_order_id": rec.id, "product_id": product.id, "quantity": 1}
    )
    assert line.van_location_id == van_a
    rec.with_user(w.ud).action_reassign(reassignment="%d A is off sick" % w.eb.id)
    assert (rec.van_location_id, line.van_location_id) == (van_b, van_b)
    # a technician with no van: no van (not the previous one)
    ec = _user(w, "erp_m02_tech_c", "cd_field_service.group_fix_field_service_user").employee_id
    certify_for_dispatch(w.env, ec)
    rec.with_user(w.ud).action_reassign(reassignment="%d B called away" % ec.id)
    assert not rec.van_location_id and not line.van_location_id
    # the van is not typed on the order
    assert refused(w.env, lambda: rec.with_user(w.ud).write({"van_location_id": van_a.id}))


# ===================================================== F10 decision log
def test_a_reassignment_is_a_logged_dispatch_decision(w, monkeypatch):
    rec = w.fo("accepted", w.ea)
    rec.with_user(w.ud).action_reassign(reassignment="%d A is off sick" % w.eb.id)
    dec = w.env["fix.dispatch.decision"].search([("field_order_id", "=", rec.id)])
    assert len(dec) == 1
    assert (dec.decision_type, dec.technician_id, dec.previous_technician_id) == (
        "reassign",
        w.eb,
        w.ea,
    )
    assert dec.decided_by_id == w.ud and dec.override_notes == "A is off sick"
    if dec.is_override:
        events = w.env["fix.event.outbox"].search(
            [("aggregate", "=", "fix.dispatch.decision"), ("aggregate_id", "=", dec.id)]
        )
        assert events.event_type == "assignment.overridden"
    # a reassignment record cannot be typed in, even by a dispatcher
    mw, _ma = p03(w, w.ud, monkeypatch)
    res = mw(
        model="fix.dispatch.decision",
        record_id=False,
        values={"field_order_id": rec.id, "technician_id": w.ea.id, "decision_type": "reassign"},
    )
    assert not res.get("id")
    assert refused(
        w.env,
        lambda: w.env["fix.dispatch.decision"]
        .with_user(w.ud)
        .create({"field_order_id": rec.id, "technician_id": w.ea.id, "decision_type": "reassign"}),
    )


# ======================================================= F11 route plan
def test_route_keeps_its_optimised_order_and_uses_its_own_depot(w):
    coords = [(23.760, 90.390), (23.860, 90.400), (23.760, 90.400), (23.850, 90.380)]
    stops = w.env["fix.field.order"].browse(
        [w.fo(latitude=la, longitude=lo).id for la, lo in coords]
    )
    route = w.env["fix.field.route"].create(
        {"technician_id": w.ea.id, "operating_unit_id": w.ou.id, "field_order_ids": stops.ids}
    )
    err = refused(w.env, lambda: route.with_user(w.ud).action_optimize_route())
    assert err and "no depot position" in err
    route.write({"depot_latitude": 23.86, "depot_longitude": 90.40})
    route.with_user(w.ud).action_optimize_route()
    order = json.loads(route.stop_sequence_json)
    assert sorted(order) == sorted(stops.ids)
    # the depot sits on the second stop: the plan starts there
    assert order[0] == stops[1].id and route.stop_plan.startswith("1. %s" % stops[1].name)
    # a different depot gives a different first stop
    route.write({"depot_latitude": 23.755, "depot_longitude": 90.389})
    assert route.route_state == "draft" and not route.stop_sequence_json
    route.with_user(w.ud).action_optimize_route()
    assert json.loads(route.stop_sequence_json)[0] == stops[0].id
    assert refused(w.env, lambda: route.with_user(w.ud).write({"stop_plan": "forged"}))


# ============================================================ F14 reports
def test_onsite_payment_report_reads_the_field_order_collection(w):
    from odoo.addons.cd_p03_portal.controllers.a02 import m02 as ctl

    so = w.so()
    rec = _completed_cash(w, so, 650)
    # a confirmed AR receipt of the same customer for another job must not
    # reconcile this cash
    rows = {r["field_order"]: r for r in ctl._field_pay_report(w.env)["rows"]}
    assert rows[rec.name]["amount"] == 650.0
    assert rows[rec.name]["status"] == "Cash still with the technician"
    rec.with_user(w.ua).action_handover_field_cash()
    rows = {r["field_order"]: r for r in ctl._field_pay_report(w.env)["rows"]}
    assert rows[rec.name]["status"] == "Cash declared, awaiting the branch cashier"
    _open_shift(w)
    rec.with_user(_user(w, "erp_m02_cashier5", *CASHIER_GROUPS)).action_accept_field_cash()
    rows = {r["field_order"]: r for r in ctl._field_pay_report(w.env)["rows"]}
    assert rows[rec.name]["status"].startswith("Reconciled")
    assert rows[rec.name]["receipt"] == "Cash shift #%s" % rec.cash_shift_id.id


def test_van_stock_report_counts_field_order_parts_on_the_van(w):
    from odoo.addons.cd_p03_portal.controllers.a02 import m02 as ctl

    van = _van(w, w.ea, "EM2VR")
    rec = w.fo("pending_dispatch")
    rec.with_user(w.ud).action_dispatch(technician_id=w.ea.id)
    product = w.env["product.product"].create({"name": "ERP M02 fuse"})
    line = w.env["fix.field.order.part"].create(
        {"field_order_id": rec.id, "product_id": product.id, "quantity": 3, "unit_cost": 10.0}
    )
    line.sudo()._guarded().write({"state": "consumed"})
    recon = (
        w.env["fix.stock.van.recon"]
        .sudo()
        .create({"location_id": van.id, "technician_id": w.ea.id})
    )
    rows = {r["recon"]: r for r in ctl._van_stock_report(w.env)["rows"]}
    assert (rows[recon.name]["consumed_qty"], rows[recon.name]["consumed_value"]) == (3.0, 30.0)


# ======================================================= F18 bridge
def test_a_field_order_from_a_service_order_is_unscheduled(w):
    so = w.so(sla_resolution_deadline=fields.Datetime.now() + timedelta(hours=6))
    fo = so.with_user(w.ud).action_create_field_order()
    assert not fo.scheduled_start and fo.sla_deadline == so.sla_resolution_deadline


# ============================================================ F21 KPIs
def test_kpis_ignore_drafts_and_unscheduled_arrivals(w):
    from odoo.addons.cd_p03_portal.controllers.a02 import m02 as ctl

    before = ctl.kpis(w.env)
    old = fields.Datetime.now() - timedelta(hours=2)
    draft = w.fo("draft")
    w.env.flush_all()  # the raw UPDATE below must not be overwritten by a later flush
    w.env.cr.execute(
        "UPDATE fix_field_order SET create_date = %s, write_date = %s WHERE id = %s",
        (old, old, draft.id),
    )
    waiting = w.fo("pending_dispatch")
    waiting.sudo()._guarded().write({"dispatch_requested_at": old})
    w.env.invalidate_all()
    after = ctl.kpis(w.env)
    assert after["unassigned_15m"] == before["unassigned_15m"] + 1
    # an arrival with no scheduled start is neither on time nor late
    unscheduled = w.fo("arrived", w.ea)
    unscheduled.sudo()._guarded().write({"arrived_at": fields.Datetime.now()})
    assert ctl.kpis(w.env)["on_time_arrival"] == before["on_time_arrival"]
    # a job completed this week counts whatever its priority or schedule
    done = w.fo("completed", w.ea, priority="0")
    done.sudo()._guarded().write({"completed_at": fields.Datetime.now()})
    assert ctl.kpis(w.env)["jobs_tech_day"] > 0


def test_the_workspace_offers_the_new_actions():
    from odoo.addons.cd_p03_portal.controllers import a02

    actions = a02.SURFACES["fix.field.order"]["actions"]
    assert {
        "action_accept_field_cash",
        "action_set_geofence",
        "action_handover_field_cash",
    } <= actions
