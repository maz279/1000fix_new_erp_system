"""cd_rental_asset behaviour (live ORM, rolled back): Journey 8 rental
reserve -> deliver -> active -> return -> damage assessment -> close, with
availability, tiered pricing, M03 logistics and deposit settlement."""

from __future__ import annotations

import json
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError, ValidationError

RES = "fix.rental.reservation"


def _events(env, event_type, res_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate", "=", RES), ("aggregate_id", "=", res_id)],
        order="id",
    )
    return [json.loads(r.payload) for r in rows]


def _device(env, name="Rental Laptop"):
    brand = env["fix.brand"].search([("name", "=", "Rental Brand (behaviour)")], limit=1)
    brand = brand or env["fix.brand"].create({"name": "Rental Brand (behaviour)", "code": "RNTB"})
    model = env["fix.device.model"].create({"name": f"{name} model", "brand_id": brand.id})
    return env["fix.device"].create({"device_model_id": model.id})


def _sku(env, **rates):
    tmpl = env["product.template"].create({"name": "Projector rental (behaviour)"})
    item = env["fix.catalogue.item"].create({"product_tmpl_id": tmpl.id})
    return env["fix.rental.sku"].create({"catalogue_item_id": item.id, **rates})


def _reservation(env, **vals):
    vals.setdefault("customer_id", env["res.partner"].create({"name": "Rental Customer"}).id)
    vals.setdefault("date_from", date(2026, 11, 1))
    vals.setdefault("date_to", date(2026, 11, 4))
    return env[RES].create(vals)


def _in(env, state, **vals):
    rec = _reservation(env, **vals)
    rec.write({"state": state})
    return rec


# --------------------------------------------------------------------------
# Creation, duration and pricing
# --------------------------------------------------------------------------


def test_create_defaults_and_name(odoo_env):
    rec = odoo_env[RES].create({"customer_id": odoo_env["res.partner"].create({"name": "C"}).id})
    # the module ships the rental sequence (data/ir_sequence.xml): a new
    # reservation is numbered, not left as the "RENT/New" placeholder
    assert rec.name.startswith("RENT/")
    assert rec.name != "RENT/New"
    assert rec.state == "draft"
    assert rec.date_from == rec.date_to == fields.Date.context_today(rec)
    assert rec.duration_days == 1
    assert rec.currency_id == odoo_env.ref("base.BDT")


def test_explicit_name_kept_and_sequence_used(odoo_env):
    assert _reservation(odoo_env, name="RENT/LEGACY/1").name == "RENT/LEGACY/1"
    # one sequence per code: retarget the module's own sequence instead of
    # creating a second row for the same code (next_by_code would be ambiguous)
    seq = odoo_env["ir.sequence"].search([("code", "=", RES)], limit=1)
    seq.prefix = "RENT/T/"
    assert _reservation(odoo_env).name.startswith("RENT/T/")


@pytest.mark.parametrize(
    ("date_from", "date_to", "days"),
    [
        (date(2026, 11, 1), date(2026, 11, 4), 4),
        (date(2026, 11, 1), date(2026, 11, 1), 1),
        (date(2026, 11, 5), date(2026, 11, 1), 1),  # inverted window never goes below 1
    ],
)
def test_duration_is_inclusive_and_at_least_one_day(odoo_env, date_from, date_to, days):
    assert _reservation(odoo_env, date_from=date_from, date_to=date_to).duration_days == days


def test_duration_without_dates_defaults_to_one(odoo_env):
    draft = odoo_env[RES].new({"date_from": False, "date_to": False})
    assert draft.duration_days == 1


@pytest.mark.parametrize(
    ("days", "rates", "charge"),
    [
        (4, {"daily_rate": 1500}, 6000),
        (10, {"daily_rate": 1500, "weekly_rate": 9000}, 9000 + 3 * 1500),
        (10, {"weekly_rate": 7000}, 7000 + 3 * 1000),  # remainder at weekly/7
        (6, {"daily_rate": 1500, "weekly_rate": 9000}, 9000),  # < 7 days: daily only
        (35, {"daily_rate": 1500, "weekly_rate": 9000, "monthly_rate": 30000}, 30000 + 5 * 1500),
        (35, {"monthly_rate": 30000}, 30000 + 5 * 1000),  # remainder at monthly/30
        (35, {"daily_rate": 1000, "weekly_rate": 6000}, 5 * 6000),  # no monthly: weekly tier
        (8, {"daily_rate": 1000}, 8000),  # no weekly: daily tier
    ],
)
def test_tiered_rental_charge(odoo_env, days, rates, charge):
    start = date(2026, 11, 1)
    rec = _reservation(odoo_env, date_from=start, date_to=start + timedelta(days=days - 1), **rates)
    assert rec.duration_days == days
    assert rec.rental_charge == pytest.approx(charge)


def test_rental_sku_onchange_copies_rates_and_deposit(odoo_env):
    sku = _sku(
        odoo_env, daily_rate=800, weekly_rate=5000, monthly_rate=18000, security_deposit=10000
    )
    rec = odoo_env[RES].new({"rental_sku_id": sku.id})
    rec._onchange_rental_sku()
    assert (rec.daily_rate, rec.weekly_rate, rec.monthly_rate) == (800, 5000, 18000)
    assert rec.deposit_collected == 10000


def test_rental_sku_onchange_keeps_negotiated_deposit(odoo_env):
    sku = _sku(odoo_env, daily_rate=800, security_deposit=10000)
    rec = odoo_env[RES].new({"rental_sku_id": sku.id, "deposit_collected": 2500})
    rec._onchange_rental_sku()
    assert rec.daily_rate == 800
    assert rec.deposit_collected == 2500


def test_rental_sku_onchange_without_sku_changes_nothing(odoo_env):
    rec = odoo_env[RES].new({"daily_rate": 999})
    rec._onchange_rental_sku()
    assert rec.daily_rate == 999
    assert rec.deposit_collected == 0


def test_damage_total_and_negative_cost_refused(odoo_env):
    rec = _reservation(odoo_env)
    dmg = odoo_env["fix.rental.damage"]
    dmg.create({"reservation_id": rec.id, "description": "Scratch", "cost": 300})
    dmg.create(
        {"reservation_id": rec.id, "description": "Charger", "cost": 1200, "category": "accessory"}
    )
    assert rec.damage_total == 1500
    with pytest.raises(ValidationError, match="cannot be negative"), odoo_env.cr.savepoint():
        dmg.create({"reservation_id": rec.id, "description": "Credit?", "cost": -1})


# --------------------------------------------------------------------------
# Reservation & availability
# --------------------------------------------------------------------------


def test_reserve_refuses_inverted_window(odoo_env):
    rec = _reservation(odoo_env, date_from=date(2026, 11, 5), date_to=date(2026, 11, 1))
    with pytest.raises(UserError, match="inverted"):
        rec.action_reserve()
    assert rec.state == "draft"


def test_reserve_without_device_publishes(odoo_env):
    rec = _reservation(odoo_env, deposit_collected=5000)
    rec.action_reserve()
    assert rec.state == "reserved"
    assert _events(odoo_env, "rental.reserved", rec.id) == [
        {
            "customer": "Rental Customer",
            "sku": "",
            "from": "2026-11-01",
            "to": "2026-11-04",
            "deposit": 5000.0,
        }
    ]


def test_reserve_reports_sku_name(odoo_env):
    sku = _sku(odoo_env)
    rec = _reservation(odoo_env, rental_sku_id=sku.id)
    rec.action_reserve()
    (payload,) = _events(odoo_env, "rental.reserved", rec.id)
    assert payload["sku"] == "Projector rental (behaviour)"


def test_reserve_blocks_overlapping_booking_of_same_device(odoo_env):
    device = _device(odoo_env)
    first = _reservation(odoo_env, device_id=device.id)
    first.action_reserve()
    clash = _reservation(
        odoo_env, device_id=device.id, date_from=date(2026, 11, 4), date_to=date(2026, 11, 8)
    )
    with pytest.raises(UserError, match="already reserved for the overlapping period"):
        clash.action_reserve()
    assert clash.state == "draft"
    # adjacent window, other device, and a re-reserve of itself are all fine
    after = _reservation(
        odoo_env, device_id=device.id, date_from=date(2026, 11, 5), date_to=date(2026, 11, 8)
    )
    after.action_reserve()
    other = _reservation(odoo_env, device_id=_device(odoo_env, "Other").id)
    other.action_reserve()
    first.action_reserve()
    assert {first.state, after.state, other.state} == {"reserved"}


def test_cancelled_booking_frees_the_device(odoo_env):
    device = _device(odoo_env)
    old = _in(odoo_env, "cancelled", device_id=device.id)
    new = _reservation(odoo_env, device_id=device.id)
    new.action_reserve()
    assert new.state == "reserved"
    assert old.state == "cancelled"


# --------------------------------------------------------------------------
# M03 logistics
# --------------------------------------------------------------------------


def test_delivery_consignment_requires_reserved(odoo_env):
    rec = _reservation(odoo_env)
    with pytest.raises(UserError, match="reserved rentals"):
        rec.action_generate_delivery_consignment()


def test_delivery_consignment_created_once_on_users_ou(odoo_env):
    """Regression: the consignment was created without its REQUIRED
    operating unit, so dispatching any rental failed in the database."""
    rec = _in(odoo_env, "reserved")
    consignment = rec.action_generate_delivery_consignment()
    assert consignment == rec.delivery_consignment_id
    assert consignment.consignment_type == "delivery"
    assert consignment.operating_unit_id == odoo_env.user.default_operating_unit_id
    assert rec.action_generate_delivery_consignment() == consignment


def test_delivery_consignment_prefers_reservation_ou(odoo_env):
    ou = odoo_env["operating.unit"].create(
        {
            "name": "Rental OU (behaviour)",
            "code": "RNT-OU",
            "partner_id": odoo_env.company.partner_id.id,
        }
    )
    rec = _in(odoo_env, "reserved", operating_unit_id=ou.id)
    assert rec.action_generate_delivery_consignment().operating_unit_id == ou


def test_delivery_consignment_for_every_reservation(odoo_env):
    """Regression: the method returned inside its loop, so only the first
    reservation of a batch got a delivery consignment."""
    recs = _in(odoo_env, "reserved") | _in(odoo_env, "reserved")
    consignments = recs.action_generate_delivery_consignment()
    assert all(recs.mapped("delivery_consignment_id"))
    assert consignments == recs.mapped("delivery_consignment_id")
    assert len(consignments) == 2


def test_logistics_without_any_operating_unit_is_refused(odoo_env):
    odoo_env.user.write({"default_operating_unit_id": False})
    rec = _in(odoo_env, "reserved")
    with pytest.raises(UserError, match="has no operating unit"):
        rec.action_generate_delivery_consignment()
    assert not rec.delivery_consignment_id


def test_return_consignment_requires_active_or_delivered(odoo_env):
    rec = _in(odoo_env, "reserved")
    with pytest.raises(UserError, match="active or delivered"):
        rec.action_generate_return_consignment()


@pytest.mark.parametrize("state", ["active", "delivered"])
def test_return_consignment_created_once(odoo_env, state):
    rec = _in(odoo_env, state)
    pickup = rec.action_generate_return_consignment()
    assert pickup.consignment_type == "pickup"
    assert pickup.operating_unit_id == odoo_env.user.default_operating_unit_id
    assert rec.action_generate_return_consignment() == pickup


def test_return_consignment_for_every_reservation(odoo_env):
    recs = _in(odoo_env, "active") | _in(odoo_env, "delivered")
    pickups = recs.action_generate_return_consignment()
    assert len(pickups) == 2
    assert pickups == recs.mapped("return_consignment_id")


# --------------------------------------------------------------------------
# Lifecycle
# --------------------------------------------------------------------------


def test_deliver_requires_reserved(odoo_env):
    rec = _reservation(odoo_env)
    with pytest.raises(UserError, match="Deliver from reserved"):
        rec.action_deliver()


def test_deliver_reports_consignment(odoo_env):
    plain = _in(odoo_env, "reserved")
    plain.action_deliver()
    assert plain.state == "delivered"
    assert _events(odoo_env, "rental.delivered", plain.id) == [
        {"customer": "Rental Customer", "consignment": ""}
    ]
    shipped = _in(odoo_env, "reserved")
    consignment = shipped.action_generate_delivery_consignment()
    shipped.action_deliver()
    assert _events(odoo_env, "rental.delivered", shipped.id)[0]["consignment"] == consignment.name


def test_activate_from_delivered_or_reserved(odoo_env):
    draft = _reservation(odoo_env)
    with pytest.raises(UserError, match="Activate from delivered or reserved"):
        draft.action_activate()
    for state in ("delivered", "reserved"):
        rec = _in(odoo_env, state)
        rec.action_activate()
        assert rec.state == "active"
        assert _events(odoo_env, "rental.activated", rec.id) == [
            {"customer": "Rental Customer", "start_date": "2026-11-01"}
        ]


def test_return_requires_active(odoo_env):
    rec = _in(odoo_env, "delivered")
    with pytest.raises(UserError, match="Return from active"):
        rec.action_return()


def test_on_time_return_has_no_late_fee(odoo_env):
    today = fields.Date.context_today(odoo_env[RES])
    rec = _in(
        odoo_env, "active", date_from=today - timedelta(days=2), date_to=today, daily_rate=500
    )
    rec.action_return()
    assert rec.state == "returned"
    assert rec.actual_return_date == today
    assert rec.late_fee == 0
    assert _events(odoo_env, "rental.returned", rec.id) == [
        {"customer": "Rental Customer", "actual_return_date": str(today), "late_fee": 0.0}
    ]


def test_late_return_charges_one_and_a_half_daily_rate(odoo_env):
    today = fields.Date.context_today(odoo_env[RES])
    rec = _in(
        odoo_env,
        "active",
        date_from=today - timedelta(days=6),
        date_to=today - timedelta(days=3),
        daily_rate=500,
    )
    rec.action_return()
    assert rec.late_fee == 3 * 500 * 1.5


def test_late_return_without_daily_rate_uses_average_charge(odoo_env):
    today = fields.Date.context_today(odoo_env[RES])
    rec = _in(
        odoo_env,
        "active",
        date_from=today - timedelta(days=11),
        date_to=today - timedelta(days=2),  # 10 days on the weekly tier
        weekly_rate=7000,
    )
    assert rec.rental_charge == 7000 + 3 * 1000
    rec.action_return()
    assert rec.late_fee == pytest.approx(2 * (10000 / 10) * 1.5)


def test_assess_damage_requires_returned(odoo_env):
    rec = _in(odoo_env, "active")
    with pytest.raises(UserError, match="Assess damage from returned"):
        rec.action_assess_damage()


def test_assess_damage_publishes_total(odoo_env):
    rec = _in(odoo_env, "returned")
    odoo_env["fix.rental.damage"].create(
        {"reservation_id": rec.id, "description": "Dent", "cost": 750}
    )
    rec.action_assess_damage()
    assert rec.state == "damage_assess"
    assert _events(odoo_env, "rental.damage_assessed", rec.id) == [{"damage_total": 750.0}]


def test_close_requires_damage_assessment(odoo_env):
    rec = _in(odoo_env, "returned")
    with pytest.raises(UserError, match="Close from damage assessment"):
        rec.action_close()


def test_close_refunds_deposit_balance(odoo_env):
    rec = _in(odoo_env, "damage_assess", deposit_collected=5000, daily_rate=1000, late_fee=300)
    odoo_env["fix.rental.damage"].create(
        {"reservation_id": rec.id, "description": "Key", "cost": 700}
    )
    rec.action_close()
    assert rec.state == "closed"
    assert rec.deposit_refunded == 4000
    assert rec.excess_billed == 0
    assert _events(odoo_env, "rental.closed", rec.id) == [
        {
            "rental_charge": 4000.0,
            "deposit_collected": 5000.0,
            "damage_total": 700.0,
            "late_fee": 300.0,
            "deduction": 1000.0,
            "refund": 4000.0,
            "excess_billed": 0.0,
        }
    ]


def test_close_bills_charges_exceeding_deposit(odoo_env):
    rec = _in(odoo_env, "damage_assess", deposit_collected=2000, late_fee=500)
    odoo_env["fix.rental.damage"].create(
        {"reservation_id": rec.id, "description": "Lost", "cost": 6000, "category": "lost"}
    )
    rec.action_close()
    assert rec.deposit_refunded == 0
    assert rec.excess_billed == 4500
    (payload,) = _events(odoo_env, "rental.closed", rec.id)
    assert payload["deduction"] == 2000.0
    assert payload["excess_billed"] == 4500.0


def test_full_journey(odoo_env):
    today = fields.Date.context_today(odoo_env[RES])
    rec = _reservation(
        odoo_env,
        device_id=_device(odoo_env, "Journey").id,
        date_from=today,
        date_to=today + timedelta(days=2),
        daily_rate=1000,
        deposit_collected=3000,
    )
    rec.action_reserve()
    rec.action_generate_delivery_consignment()
    rec.action_deliver()
    rec.action_activate()
    rec.action_generate_return_consignment()
    rec.action_return()
    rec.action_assess_damage()
    rec.action_close()
    assert rec.state == "closed"
    assert rec.rental_charge == 3000
    assert rec.deposit_refunded == 3000
    assert rec.delivery_consignment_id.consignment_type == "delivery"
    assert rec.return_consignment_id.consignment_type == "pickup"
