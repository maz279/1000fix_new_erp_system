"""A02 pass 2 (owner decisions D1 / D20, M03-02 / M03-08): service-order COD
in the rider's settlement, and the rider's hand-in deadline.

D1: a repaired device may go home on a cash-on-delivery leg. The rider
collects the order's amount due (fix.consignment.cod_amount); the order
records it with tender "cod" and its receipt debits COD clearing; the rider
settlement loads those legs beside storefront orders, credits COD clearing for
both, and verifies each order's COD settlement when it is settled.
D20: a rider holding delivered COD not in a settlement by the end of the next
business day gets no new COD and logistics + finance are told (daily cron).

Uses the A08 M50 fixture (``c``): accountant / accounting administrators, not
the superuser. ``odoo_env`` rolls back.
"""

# ruff: noqa: F811  (the A08 fixture `c` is imported and used as a parameter)
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError

from .test_a08_m50_controls import _cod, _cod_orders, bal, c  # noqa: F401 - fixture

pytestmark = [pytest.mark.financial]

BILLING = "cd_billing_engine.account_code."


@pytest.fixture
def so(c):
    env = c.env
    params = env["ir.config_parameter"].sudo()
    ar = env["account.account"].create(
        {"code": "R2SOAR%d" % c.n, "name": "R2 receivable", "account_type": "asset_receivable"}
    )
    params.set_param(BILLING + "ar", ar.code)
    params.set_param(BILLING + "cod_clearing", c.acc["cod_clearing"].code)
    brand = env["fix.brand"].create({"name": "R2COD%d" % c.n, "code": "R2C%d" % c.n})
    model = env["fix.device.model"].create({"name": "R2 COD phone", "brand_id": brand.id})
    c.customer = env["res.partner"].create({"name": "R2 COD customer %d" % c.n})
    c.rider.work_contact_id = env["res.partner"].create({"name": "R2 rider contact"})

    def order(price=1000.0):
        device = env["fix.device"].create({"device_model_id": model.id, "owner_id": c.customer.id})
        o = env["fix.service.order"].create(
            {
                "device_id": device.id,
                "customer_id": c.customer.id,
                "branch_id": c.branch.id,
                "operating_unit_id": c.ou.id,
                "fault_description": "COD delivery",
                "state": "ready",
            }
        )
        env["fix.estimate"].create(
            {
                "order_id": o.id,
                "state": "approved",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "description": "Repair",
                            "quantity": 1,
                            "unit_price": price,
                            "line_type": "labour",
                        },
                    )
                ],
            }
        )
        return o

    def leg(o, amount, delivered_days_ago=0, record=True):
        cons = (
            env["fix.consignment"]
            .sudo()
            .create(
                {
                    "operating_unit_id": c.ou.id,
                    "consignment_type": "delivery",
                    "scheduled_date": fields.Datetime.now(),
                    "rider_id": c.rider.id,
                    "service_order_id": o.id,
                }
            )
        )
        when = fields.Datetime.now() - timedelta(days=delivered_days_ago)
        env.cr.execute(
            "UPDATE fix_consignment SET state = 'delivered', delivered_at = %s, cod_amount = %s, "
            "pod_verified_at = %s WHERE id = %s",
            (when, amount, when, cons.id),
        )
        cons.invalidate_recordset()
        if record:
            record_cod(o, amount, "COD/%s" % cons.name)
        return cons

    def record_cod(o, amount, ref):
        """The order records the rider's collection (interface contract:
        source "cod"). Without S1's source in this worktree the recorded
        state is written as S1 leaves it (settled, unverified, tender cod)
        and the receipt raised by the same S2 hook the settlement calls."""
        Order = env["fix.service.order"]
        if "cod" in dict(Order._fields["settlement_source"].selection):
            o.with_context(fd_settlement_tender="cod")._fix_record_settlement(
                amount, ref, source="cod"
            )
            return
        o._guarded().write(
            {
                "payment_settlement_state": "settled",
                "invoice_ref": ref,
                "amount_settled_bdt": amount,
                "settlement_source": "field_collection",
                "settlement_tender": "cod",
                "settlement_verified": False,
            }
        )
        o._fdf_raise_settlement_receipt(amount, tender="cod", reference=ref)

    c.order, c.leg = order, leg
    return c


def test_the_rider_settles_service_order_cod_and_verifies_it(so):
    c = so
    o = c.order()
    due = o._fix_amount_due()
    leg = c.leg(o, due)
    receipt = c.env["fix.ar.receipt"].search([("source_order_id", "=", o.id)])
    assert receipt.method == "cod" and bal(c, c.acc["cod_clearing"]) == due
    assert not o.settlement_verified
    s = _cod(c, c.acct)
    s.with_user(c.acct).action_load_orders()
    assert leg in s.consignment_ids and s.expected_amount == due
    s.with_user(c.acct).write({"remitted_amount": due})
    s.with_user(c.acct).action_submit()
    s.with_user(c.mgr).action_settle()
    assert s.state == "settled"
    # COD clearing is relieved and the order's settlement is verified
    assert bal(c, c.acc["cod_clearing"]) == 0.0
    o.invalidate_recordset()
    assert o.settlement_verified
    # one leg, one settlement
    again = _cod(c, c.acct)
    again.with_user(c.acct).action_load_orders()
    assert leg not in again.consignment_ids


def test_an_unrecorded_collection_is_not_settled(so):
    c = so
    o = c.order()
    leg = c.leg(o, o._fix_amount_due(), record=False)
    s = _cod(c, c.acct)
    s.with_user(c.acct).action_load_orders()
    assert leg not in s.consignment_ids  # nothing to settle against yet
    s.sudo()._guarded().write({"consignment_ids": [(4, leg.id)]})
    s.with_user(c.acct).write({"remitted_amount": 100.0})
    with pytest.raises(UserError, match="not recorded"):
        s.with_user(c.acct).action_submit()


def test_cod_held_past_the_next_business_day_blocks_the_rider(so):
    c = so
    Settlement = c.env["fix.cod.settlement"]
    o = c.order()
    c.leg(o, o._fix_amount_due(), delivered_days_ago=0)
    assert not Settlement._fix_rider_has_open_variance(c.rider)
    o2 = c.order()
    late = c.leg(o2, o2._fix_amount_due(), delivered_days_ago=4)
    assert Settlement._fix_rider_has_open_variance(c.rider)
    # no new COD leg for the rider
    fresh = (
        c.env["fix.consignment"]
        .sudo()
        .create(
            {
                "operating_unit_id": c.ou.id,
                "consignment_type": "delivery",
                "scheduled_date": fields.Datetime.now(),
                "service_order_id": c.order().id,
            }
        )
    )
    fresh.cod_amount = 500.0
    with pytest.raises(UserError, match="blocked"):
        fresh.write({"rider_id": c.rider.id})
    # the daily job tells finance (and logistics) once
    assert Settlement._cron_cod_handin_overdue() >= 1
    Settlement._cron_cod_handin_overdue()
    acts = c.rider.sudo().activity_ids.filtered(lambda a: a.summary == "Rider COD hand-in overdue")
    assert acts and len(acts) == len(acts.mapped("user_id"))
    # once settled, the block lifts
    s = _cod(c, c.acct)
    s.with_user(c.acct).action_load_orders()
    assert late in s.consignment_ids
    assert not Settlement._fix_rider_has_open_variance(c.rider)


def test_the_hand_in_deadline_skips_the_weekend(so):
    c = so
    Settlement = c.env["fix.cod.settlement"]
    thursday = fields.Date.to_date("2026-11-19")
    assert thursday.weekday() == 3
    # delivered Thursday: Friday is the weekend, Saturday is the deadline
    assert Settlement._fix_handin_deadline(thursday) == fields.Date.to_date("2026-11-21")


def test_the_cod_receipt_books_only_the_balance_of_a_part_paid_order(so):
    """A02 pass 2 review (COD contract): the COD receipt counted the money
    recorded before only when that was COD too, so the balance of an order
    part-paid on site in cash debited COD clearing with the technician's part
    as well, and the rider's remittance could never clear it."""
    c = so
    o = c.order(1000.0)
    due = o._fix_amount_due()
    balance = round(due - 300.0, 2)
    o.with_context(fd_settlement_tender="cash")._fix_record_settlement(
        300.0, "FIELD/R2-PART", source="field_collection"
    )
    assert o.payment_settlement_state == "partial" and o._fix_amount_outstanding() == balance
    leg = c.leg(o, balance)
    receipt = c.env["fix.ar.receipt"].search(
        [("source_order_id", "=", o.id), ("method", "=", "cod")]
    )
    assert receipt.amount == balance and receipt.reference == "COD/%s" % leg.name
    assert bal(c, c.acc["cod_clearing"]) == balance
    assert o.payment_settlement_state == "settled" and o.amount_settled_bdt == due


def test_the_rider_settlement_hands_in_the_legs_cod(so):
    """A02 pass 2 review (rider COD): an own rider's leg is handed in by the
    rider's COD settlement; without cod_remitted_at on the leg, cd_consignment
    blocked the rider from every new leg from day 2, for ever."""
    c = so
    o = c.order()
    due = o._fix_amount_due()
    leg = c.leg(o, due, delivered_days_ago=4)
    # the collection at the POD (cd_consignment stamps it)
    c.env.cr.execute(
        "UPDATE fix_consignment SET cod_collected_at = delivered_at WHERE id = %s", (leg.id,)
    )
    leg.invalidate_recordset()
    Leg = c.env["fix.consignment"]
    assert leg in Leg._m03_overdue_cod_legs(c.rider)
    with pytest.raises(UserError, match="hand-in deadline"):
        Leg._m03_refuse_overdue_cod_rider(c.rider.id)
    s = _cod(c, c.acct)
    s.with_user(c.acct).action_load_orders()
    assert leg in s.consignment_ids
    s.with_user(c.acct).write({"remitted_amount": due})
    s.with_user(c.acct).action_submit()
    s.with_user(c.mgr).action_settle()
    leg.invalidate_recordset()
    assert leg.cod_remitted_at
    assert not Leg._m03_overdue_cod_legs(c.rider)
    Leg._m03_refuse_overdue_cod_rider(c.rider.id)  # no longer blocked


def _overdue_leg(c, o, amount, days=4):
    """A delivered own-rider COD leg, its collection recorded on the order
    ``days`` ago (cd_consignment stamps cod_collected_at at the POD)."""
    leg = c.leg(o, amount, delivered_days_ago=days)
    c.env.cr.execute(
        "UPDATE fix_consignment SET cod_collected_at = delivered_at WHERE id = %s", (leg.id,)
    )
    leg.invalidate_recordset()
    return leg


def _settle(c, amount):
    s = _cod(c, c.acct)
    s.with_user(c.acct).action_load_orders()
    s.with_user(c.acct).write({"remitted_amount": amount})
    s.with_user(c.acct).action_submit()
    s.with_user(c.mgr).action_settle()
    return s


def test_n1_a_cod_balance_after_a_verified_part_payment_is_settled(so):
    """A02 pass 2 review N1: a part payment taken on site and accepted by a
    cashier left the order's tender 'cash'; the COD balance then never
    counted as recorded, the leg was never settled, the rider stayed blocked
    and the order never closed."""
    c = so
    o = c.order()
    due = o._fix_amount_due()
    # setup: BDT 300 taken on site and counted in by a cashier (verified)
    o._guarded().write(
        {
            "payment_settlement_state": "partial",
            "amount_settled_bdt": 300.0,
            "amount_verified_bdt": 300.0,
            "settlement_verified": True,
            "settlement_source": "field_collection",
            "settlement_tender": "cash",
            "invoice_ref": "COD/FO-N1",
        }
    )
    rest = round(due - 300.0, 2)
    leg = _overdue_leg(c, o, rest)
    assert (o.settlement_source, o.settlement_tender) == ("cod", "cash")
    Leg = c.env["fix.consignment"]
    assert leg in Leg._m03_overdue_cod_legs(c.rider)
    s = _settle(c, rest)
    assert leg in s.consignment_ids and s.state == "settled"
    o.invalidate_recordset()
    assert o.settlement_verified and o.amount_verified_bdt == due
    assert not Leg._m03_overdue_cod_legs(c.rider)
    assert not c.env["fix.cod.settlement"]._fix_rider_has_open_variance(c.rider)
    Leg._m03_refuse_overdue_cod_rider(c.rider.id)
    assert not o._fix_close_problem()


def test_n2_the_rider_settlement_confirms_only_the_cod_part(so):
    """A02 pass 2 review N2: confirming the COD verified the whole settled
    amount, an unchecked bKash part payment (with no receipt) included."""
    c = so
    o = c.order()
    due = o._fix_amount_due()
    o.with_context(fd_settlement_tender="bkash")._fix_record_settlement(
        200.0, "BKASH-N2", source="field_collection"
    )
    assert o.payment_settlement_state == "partial" and not o.settlement_verified
    rest = round(due - 200.0, 2)
    c.leg(o, rest)
    _settle(c, rest)
    o.invalidate_recordset()
    assert o.amount_verified_bdt == rest and not o.settlement_verified
    assert "not verified" in o._fix_close_problem()


def test_n4_an_unhanded_cod_is_not_cancelled(so):
    """A02 pass 2 review N4: cancelling voided a COD the rider really holds as
    an unverified claim, orphaning the leg, the COD clearing and the AR."""
    c = so
    o = c.order()
    due = o._fix_amount_due()
    c.leg(o, due)
    with pytest.raises(UserError, match="not handed in"), c.env.cr.savepoint():
        o.action_cancel(reason_code="customer_declined")
    o.invalidate_recordset()
    assert (o.payment_settlement_state, o.amount_settled_bdt) == ("settled", due)
    assert o.state != "cancelled"


def test_n5_a_cod_leg_after_a_price_rise_is_a_top_up(so):
    """A02 pass 2 review N5: a paid order whose estimate went up went out on a
    COD leg for the difference; the top-up refused source 'cod' at the door."""
    c = so
    o = c.order(1000.0)
    paid = o._fix_amount_due()
    o._guarded().write(
        {
            "payment_settlement_state": "settled",
            "amount_settled_bdt": paid,
            "amount_verified_bdt": paid,
            "settlement_verified": True,
            "settlement_source": "counter",
            "settlement_tender": "cash",
            "invoice_ref": "POS-N5",
        }
    )
    line = {
        "description": "Repair, revised",
        "quantity": 1,
        "unit_price": 1500.0,
        "line_type": "labour",
    }
    c.env["fix.estimate"].create(
        {"order_id": o.id, "state": "approved", "line_ids": [(0, 0, line)]}
    )
    due = o._fix_amount_due()
    assert due > paid
    short = round(due - paid, 2)
    leg = c.leg(o, short)
    assert (o.settlement_source, o.settlement_verified) == ("cod", False)
    assert (o.amount_settled_bdt, o.amount_verified_bdt) == (due, paid)
    receipt = c.env["fix.ar.receipt"].search(
        [("source_order_id", "=", o.id), ("method", "=", "cod")]
    )
    assert receipt.amount == short and receipt.reference == "COD/%s" % leg.name


def test_a_leg_in_a_submitted_settlement_no_longer_blocks_the_rider(so):
    """A02 pass 2 review: cd_consignment kept a rider blocked while his
    settlement waited for its approver; the settlement's own check did not."""
    c = so
    o = c.order()
    due = o._fix_amount_due()
    leg = _overdue_leg(c, o, due)
    Leg = c.env["fix.consignment"]
    assert leg in Leg._m03_overdue_cod_legs(c.rider)
    s = _cod(c, c.acct)
    s.with_user(c.acct).action_load_orders()
    s.with_user(c.acct).write({"remitted_amount": due})
    s.with_user(c.acct).action_submit()
    assert s.state == "submitted" and not leg.cod_remitted_at
    assert leg not in Leg._m03_overdue_cod_legs(c.rider)
    Leg._m03_refuse_overdue_cod_rider(c.rider.id)
