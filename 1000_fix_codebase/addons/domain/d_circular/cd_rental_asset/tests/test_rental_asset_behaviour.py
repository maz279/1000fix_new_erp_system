"""cd_rental_asset behaviour (live ORM, rolled back): Journey 8 rental
reserve -> deliver -> active -> return -> damage assessment -> close, with
availability, tiered pricing, M03 logistics and deposit settlement."""

from __future__ import annotations

import json
from datetime import date, timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.addons.cd_service_order.tests.test_a02_p0_m01 import order as service_order
from odoo.addons.cd_service_order.tests.test_a02_p0_m01 import w  # noqa: F401
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


# M13 capture pass 2 (2026-11-19): a rental needs a party with a verified M33
# identity (BRU-RNT-20) and photographed condition reports (BRU-RNT-01).
_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="


def _kyc(env, partner):
    env["fix.identity.document"].sudo().create(
        {"partner_id": partner.id, "document_type": "nid_10", "verification_status": "verified"}
    )
    return partner


def _photo(env, condition, view="front"):
    att = (
        env["ir.attachment"]
        .sudo()
        .create({"name": "%s.png" % view, "datas": _PNG, "mimetype": "image/png"})
    )
    return env["fix.rental.condition.photo"].create(
        {"condition_id": condition.id, "attachment_id": att.id, "view_code": view}
    )


def _branch(env):
    """A05 FIN-09: a rental's money posts to its booking branch's unit."""
    branch = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if branch:
        return branch
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1) or env[
        "fix.entity"
    ].create(
        {"legal_name": "Rental Entity (behaviour)", "code": "RNTBE", "company_id": env.company.id}
    )
    return env["fix.branch"].create(
        {
            "name": "Rental Branch (behaviour)",
            "code": "RNTB-BR",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )


def _priced_sku(env):
    """A05 M13-01: a confirmed booking is priced by its rental SKU."""
    return _sku(env, daily_rate=1000)


def _reservation(env, **vals):
    vals.setdefault(
        "customer_id", _kyc(env, env["res.partner"].create({"name": "Rental Customer"})).id
    )
    vals.setdefault("date_from", date(2026, 11, 1))
    vals.setdefault("date_to", date(2026, 11, 4))
    return env[RES].create(vals)


def _in(env, state, **vals):
    rec = _reservation(env, **vals)
    rec.write({"state": state})
    return rec


# A05 audit: handover and close need evidence. These superuser fixtures lay
# it down directly (trusted data load); the A05 behaviour suite proves the
# same gates as non-admin users through the real actions.
def _signed(env, rec):
    rec.write({"agreement_state": "signed", "stamp_duty_cert_no": "STAMP-0001"})
    return rec


def _report(env, rec, report_type):
    cond = env["fix.rental.condition"].create(
        {"reservation_id": rec.id, "report_type": report_type}
    )
    _photo(env, cond)
    return cond


def _posted_deposit(env, rec, amount):
    return env["fix.rental.deposit"].create(
        {"reservation_id": rec.id, "kind": "collect", "amount": amount, "gl_state": "posted"}
    )


def _ready_to_close(env, rec, collected=0.0, late_mode="invoice"):
    _signed(env, rec)
    _report(env, rec, "post_return")
    if collected:
        _posted_deposit(env, rec, collected)
    param = env["ir.config_parameter"]
    # the arithmetic under test, not the charge approval (test_a05_m13_* prove it)
    param.set_param("cd_rental_asset.damage_charge_requires_approval", "0")
    param.set_param("cd_rental_asset.late_fee_settlement", late_mode)
    if not rec.branch_id:
        rec.write({"branch_id": _branch(env).id})
    billable, billed = rec._unbilled()
    if billable - billed > 0.005:
        rec.action_issue_rental_invoice()
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
        (10, {"weekly_rate": 7000}, 2 * 7000),  # no daily rate: a whole week
        (6, {"daily_rate": 1500, "weekly_rate": 9000}, 9000),  # a week = 6 days
        (35, {"daily_rate": 1500, "weekly_rate": 9000, "monthly_rate": 30000}, 30000 + 5 * 1500),
        (35, {"monthly_rate": 30000}, 2 * 30000),  # no daily/weekly: a whole month
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


def test_reserve_without_any_unit_is_refused(odoo_env):
    """A05 M13-5: a booking that names no asset, device or SKU has nothing
    to check availability against; it used to be reserved unchecked."""
    rec = _reservation(odoo_env, deposit_collected=5000)
    with pytest.raises(UserError, match="names no fleet asset, device or rental SKU"):
        rec.action_reserve()
    assert rec.state == "draft"


def test_reserve_with_device_publishes(odoo_env):
    rec = _reservation(
        odoo_env,
        deposit_collected=5000,
        device_id=_device(odoo_env).id,
        rental_sku_id=_priced_sku(odoo_env).id,
        branch_id=_branch(odoo_env).id,
    )
    rec.action_reserve()
    assert rec.state == "reserved"
    assert _events(odoo_env, "rental.reserved", rec.id) == [
        {
            "customer": "Rental Customer",
            "sku": "Projector rental (behaviour)",
            "from": "2026-11-01",
            "to": "2026-11-04",
            "deposit": 5000.0,
        }
    ]


def test_reserve_reports_sku_name(odoo_env):
    sku = _sku(odoo_env, daily_rate=1000)
    # the SKU pool needs a unit: a SKU with no fleet asset is fully booked
    odoo_env["fix.rental.asset"].create({"name": "SKU-UNIT-1", "rental_sku_id": sku.id})
    rec = _reservation(odoo_env, rental_sku_id=sku.id, branch_id=_branch(odoo_env).id)
    rec.action_reserve()
    (payload,) = _events(odoo_env, "rental.reserved", rec.id)
    assert payload["sku"] == "Projector rental (behaviour)"


def test_reserve_blocks_overlapping_booking_of_same_device(odoo_env):
    device = _device(odoo_env)
    sku, branch = _priced_sku(odoo_env), _branch(odoo_env)
    priced = {"rental_sku_id": sku.id, "branch_id": branch.id}
    first = _reservation(odoo_env, device_id=device.id, **priced)
    first.action_reserve()
    clash = _reservation(
        odoo_env,
        device_id=device.id,
        date_from=date(2026, 11, 4),
        date_to=date(2026, 11, 8),
        **priced,
    )
    with pytest.raises(UserError, match="already reserved for the overlapping period"):
        clash.action_reserve()
    assert clash.state == "draft"
    # adjacent window, other device, and a re-reserve of itself are all fine
    after = _reservation(
        odoo_env,
        device_id=device.id,
        date_from=date(2026, 11, 5),
        date_to=date(2026, 11, 8),
        **priced,
    )
    after.action_reserve()
    other = _reservation(odoo_env, device_id=_device(odoo_env, "Other").id, **priced)
    other.action_reserve()
    # a second reserve would take the deposit twice: it is refused
    with pytest.raises(UserError, match="Reserve from draft"):
        first.action_reserve()
    assert {first.state, after.state, other.state} == {"reserved"}


def test_cancelled_booking_frees_the_device(odoo_env):
    device = _device(odoo_env)
    old = _in(odoo_env, "cancelled", device_id=device.id)
    new = _reservation(
        odoo_env,
        device_id=device.id,
        rental_sku_id=_priced_sku(odoo_env).id,
        branch_id=_branch(odoo_env).id,
    )
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


def _handover_ready(env, rec):
    _signed(env, rec)
    _report(env, rec, "pre_delivery")
    return rec


def test_deliver_reports_consignment(odoo_env):
    plain = _handover_ready(odoo_env, _in(odoo_env, "reserved", device_id=_device(odoo_env).id))
    plain.action_deliver()
    assert plain.state == "delivered"
    assert _events(odoo_env, "rental.delivered", plain.id) == [
        {"customer": "Rental Customer", "consignment": ""}
    ]
    shipped = _handover_ready(
        odoo_env, _in(odoo_env, "reserved", device_id=_device(odoo_env, "Shipped").id)
    )
    consignment = shipped.action_generate_delivery_consignment()
    shipped.action_deliver()
    assert _events(odoo_env, "rental.delivered", shipped.id)[0]["consignment"] == consignment.name


def test_activate_only_from_delivered(odoo_env):
    """A05 M13-17: activating straight from reserved skipped the handover."""
    for state in ("draft", "reserved"):
        with pytest.raises(UserError, match="Activate from delivered"):
            _in(odoo_env, state).action_activate()
    rec = _signed(odoo_env, _in(odoo_env, "delivered"))
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
        odoo_env,
        "active",
        date_from=today - timedelta(days=2),
        date_to=today,
        daily_rate=500,
        branch_id=_branch(odoo_env).id,
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
        branch_id=_branch(odoo_env).id,
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
        branch_id=_branch(odoo_env).id,
    )
    assert rec.rental_charge == 2 * 7000  # A05 M13-11: whole weeks, no free days
    rec.action_return()
    assert rec.late_fee == pytest.approx(2 * (14000 / 10) * 1.5)


def test_assess_damage_requires_returned(odoo_env):
    rec = _in(odoo_env, "active")
    with pytest.raises(UserError, match="Assess damage from returned"):
        rec.action_assess_damage()


def test_assess_damage_publishes_total(odoo_env):
    rec = _in(odoo_env, "returned")
    _report(odoo_env, rec, "post_return")
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


@pytest.mark.parametrize(
    ("late_mode", "deduction", "refund"),
    [
        # A05 M13-4 / M13-09: the late fee is charged ONCE, on the invoice with
        # M51 VAT; the old 'deposit' switch no longer takes it from the deposit
        ("invoice", 700.0, 4300.0),
        ("deposit", 700.0, 4300.0),
    ],
)
def test_close_refunds_deposit_balance(odoo_env, late_mode, deduction, refund):
    rec = _in(odoo_env, "damage_assess", deposit_collected=5000, daily_rate=1000, late_fee=300)
    _ready_to_close(odoo_env, rec, collected=5000, late_mode=late_mode)
    odoo_env["fix.rental.damage"].create(
        {"reservation_id": rec.id, "description": "Key", "cost": 700}
    )
    rec.action_close()
    assert rec.state == "closed"
    assert rec.deposit_refunded == refund
    assert rec.excess_billed == 0
    assert _events(odoo_env, "rental.closed", rec.id) == [
        {
            "rental_charge": 4000.0,
            "deposit_collected": 5000.0,
            "damage_total": 700.0,
            "late_fee": 300.0,
            "deduction": deduction,
            "refund": refund,
            "excess_billed": 0.0,
        }
    ]


def test_close_refund_comes_from_the_posted_ledger(odoo_env):
    """A05 M13-3: the refund used deposit_collected, so a typed 50,000 on a
    5,000 collection queued a 50,000 refund. The ledger decides."""
    rec = _in(odoo_env, "damage_assess", deposit_collected=50000)
    _ready_to_close(odoo_env, rec, collected=5000)
    rec.action_close()
    assert rec.deposit_refunded == 5000


@pytest.mark.parametrize(("late_mode", "excess"), [("invoice", 4000.0), ("deposit", 4000.0)])
def test_close_bills_charges_exceeding_deposit(odoo_env, late_mode, excess):
    rec = _in(odoo_env, "damage_assess", deposit_collected=2000, late_fee=500)
    _ready_to_close(odoo_env, rec, collected=2000, late_mode=late_mode)
    odoo_env["fix.rental.damage"].create(
        {"reservation_id": rec.id, "description": "Lost", "cost": 6000, "category": "lost"}
    )
    rec.action_close()
    assert rec.deposit_refunded == 0
    assert rec.excess_billed == excess
    (payload,) = _events(odoo_env, "rental.closed", rec.id)
    assert payload["deduction"] == 2000.0
    assert payload["excess_billed"] == excess
    # A05 M13-13: the excess reaches M20 as an invoice
    invoice = rec.excess_invoice_id
    assert invoice and invoice.state == "draft"
    assert invoice.total_payable == pytest.approx(excess)
    assert rec.damage_ids.invoice_id == invoice


def test_full_journey(odoo_env):
    today = fields.Date.context_today(odoo_env[RES])
    branch = _branch(odoo_env)
    ou = branch.operating_unit_id
    customer = _kyc(
        odoo_env,
        odoo_env["res.partner"].create({"name": "Rental Customer", "phone": "01711000444"}),
    )
    rec = _reservation(
        odoo_env,
        customer_id=customer.id,
        device_id=_device(odoo_env, "Journey").id,
        rental_sku_id=_priced_sku(odoo_env).id,
        date_from=today,
        date_to=today + timedelta(days=2),
        daily_rate=1000,
        deposit_collected=3000,
        operating_unit_id=ou.id,
        branch_id=branch.id,
        stamp_duty_cert_no="STAMP-0001",
    )
    codes = []
    with mock.patch.object(
        fix_otp_util, "dispatch_otp", lambda phone, code, ttl, language="bn": codes.append(code)
    ):
        rec.action_send_agreement()
    assert rec.action_sign_agreement(code=codes[-1]) == {"verified": True}
    rec.action_reserve()
    assert rec.deposit_ids.gl_state == "posted", rec.deposit_ids.gl_note
    rec.action_generate_delivery_consignment()
    _report(odoo_env, rec, "pre_delivery")
    rec.action_deliver()
    rec.action_activate()
    rec.action_generate_return_consignment()
    rec.action_return()
    _report(odoo_env, rec, "post_return")
    rec.action_assess_damage()
    rec.action_close()
    assert rec.state == "closed"
    # returned on its first day of three: an early return is charged for the
    # day used (A05 M13-18, minimum hire 1 day)
    assert rec.rental_charge == 1000 and rec.billable_days == 1
    assert rec.deposit_refunded == 3000
    assert rec.delivery_consignment_id.consignment_type == "delivery"
    assert rec.return_consignment_id.consignment_type == "pickup"


def test_a_loaner_leg_is_not_the_repaired_devices_leg(odoo_env, w):  # noqa: F811
    """A02 pass 2 review (P2): a loaner for a repair was dispatched on a leg
    naming the repair's service order, so it took that order's payment gate
    and COD (D1), its door serial check, and its one-live-leg slot (the
    repaired device's own leg was then refused). The loaner's legs carry no
    service order; the reservation keeps the link."""
    order = service_order(w)
    live = odoo_env["fix.consignment"].create(
        {
            "consignment_type": "pickup",
            "service_order_id": order.id,
            "scheduled_date": fields.Datetime.now(),
            "operating_unit_id": odoo_env.user.default_operating_unit_id.id,
        }
    )
    rec = _in(odoo_env, "reserved", service_order_id=order.id)
    leg = rec.action_generate_delivery_consignment()
    assert leg and not leg.service_order_id
    assert not (leg.cod_amount if "cod_amount" in leg._fields else 0.0)
    assert rec.service_order_id == order and live.state == "draft"
