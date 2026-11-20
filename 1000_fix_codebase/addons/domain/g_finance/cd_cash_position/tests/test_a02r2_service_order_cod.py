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
