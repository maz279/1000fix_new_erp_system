"""A07 P1 hand-offs (cd_asset_finance_hse_bridge): M17/M45/M46/M47 events and
register changes reach M09, M49, M52, M59 and M60.

Live ORM, rolled back. Every event is delivered through the REGISTERED
subscription (its fix.event.consumer row) by the relay's own delivery step,
the way cron_relay does it. Where the source module's real path is cheap the
event comes from it (lease record and modification extract, site and vehicle
incidents, the safety cron, device owner and warranty changes, register
creates); otherwise the event is published with the contract's payload on a
real source record. Decisions are taken as NON-ADMIN users holding the role
they would really hold (accountant, HSE officer), and refused without it.
"""

from __future__ import annotations

import json
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

REFUSED = (UserError, ValidationError, AccessError)
MOD = "cd_asset_finance_hse_bridge"
ACCOUNTANT = "account.group_account_user"
HSE = "cd_hse.group_hse_officer"
FM = "cd_facility.group_facility_manager"

CONSUMERS = {
    "consumer_equipment_written_off": ("equipment.written_off", "fix.asset.finance.request"),
    "consumer_lease_recorded": ("lease.recorded", "fix.lease"),
    "consumer_lease_extract_published": ("lease.extract_published", "fix.lease"),
    "consumer_facility_work_order_closed": ("facility.work_order_closed", "fix.asset.cost.entry"),
    "consumer_vehicle_fuel_recorded": ("vehicle.fuel_recorded", "fix.asset.cost.entry"),
    "consumer_vehicle_service_completed": ("vehicle.service_completed", "fix.asset.cost.entry"),
    "consumer_site_incident": ("site.incident", "fix.hse.incident"),
    "consumer_vehicle_incident": ("vehicle.incident", "fix.hse.incident"),
    "consumer_site_safety_equipment_unfit": ("site.safety_equipment_unfit", "fix.hse.hazard"),
    "consumer_site_risk_exception_raised": ("site.risk_exception_raised", "fix.risk.register"),
    "consumer_site_risk_decision_recorded": ("site.risk_decision_recorded", "fix.risk.register"),
    "consumer_site_compliance_expired": ("site.compliance_expired", "fix.risk.register"),
    "consumer_driver_licence_expired": ("driver.licence_expired", "fix.risk.register"),
    "consumer_vehicle_document_expired": ("vehicle.document_expired", "fix.risk.register"),
    "consumer_device_transferred": ("device.transferred", "fix.warranty.claim"),
    "consumer_device_warranty_updated": ("device.warranty_updated", "fix.warranty.claim"),
}


def _user(env, login, company, ou, *groups, employee=False):
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, ids)],
                "company_ids": [(6, 0, company.ids)],
                "company_id": company.id,
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    if employee:
        env["hr.employee"].create({"name": login, "user_id": user.id, "company_id": company.id})
    return user


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fields.Date.context_today(env["fix.site"])
    x.co = env["res.company"].create({"name": "A07P1 Bridge Co"})
    x.ou = env["operating.unit"].create(
        {
            "name": "A07P1 Bridge OU",
            "code": "A7P1BRG",
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    x.clerk = _user(env, "a07p1_brg_clerk", x.co, x.ou)
    x.acct = _user(env, "a07p1_brg_acct", x.co, x.ou, ACCOUNTANT)
    x.hse = _user(env, "a07p1_brg_hse", x.co, x.ou, HSE)
    x.hse2 = _user(env, "a07p1_brg_hse2", x.co, x.ou, HSE)
    x.fm = _user(env, "a07p1_brg_fm", x.co, x.ou, FM, employee=True)
    x.site = env["fix.site"].create(
        {
            "name": "A07P1 Bridge Branch",
            "company_id": x.co.id,
            "operating_unit_id": x.ou.id,
            "state": "active",
        }
    )
    x.landlord = env["res.partner"].create({"name": "A07P1 Bridge Landlord"})
    x.vendor = env["res.partner"].create({"name": "A07P1 Bridge Vendor"})
    x.category = env["fix.asset.category"].create(
        {"name": "A07P1 Test Equipment", "code": "A7TE", "company_id": x.co.id}
    )
    return x


def _cost_item(c, amount):
    """A08 BRU-FXA-01: an asset enters the register with its ledger consequence, so
    accepting a capitalisation names the posted journal item carrying its cost."""
    env = c.env
    if not c.category.asset_account_id:
        c.category.asset_account_id = env["account.account"].create(
            {
                "code": "A7A%s" % c.co.id,
                "name": "A07 Test Asset Account",
                "account_type": "asset_fixed",
                "company_ids": [(6, 0, c.co.ids)],
            }
        )
    # this fixture's company is brand new: it has no chart or journal of its own
    other = env["account.account"].search(
        [("account_type", "=", "asset_current"), ("company_ids", "in", c.co.id)], limit=1
    ) or env["account.account"].create(
        {
            "code": "A7C%s" % c.co.id,
            "name": "A07 Test Clearing",
            "account_type": "asset_current",
            "company_ids": [(6, 0, c.co.ids)],
        }
    )
    journal = env["account.journal"].search(
        [("type", "=", "general"), ("company_id", "=", c.co.id)], limit=1
    ) or env["account.journal"].create(
        {"name": "A07 Test", "code": "A7GL", "type": "general", "company_id": c.co.id}
    )
    move = env["account.move"].create(
        {
            "journal_id": journal.id,
            "company_id": c.co.id,
            "line_ids": [
                (
                    0,
                    0,
                    {"account_id": c.category.asset_account_id.id, "name": "cost", "debit": amount},
                ),
                (0, 0, {"account_id": other.id, "name": "cost", "credit": amount}),
            ],
        }
    )
    move.action_post()
    return move.line_ids.filtered(lambda line: line.debit)


def _as(c, user, model):
    ctx = dict(c.env.context, allowed_company_ids=c.co.ids)
    return c.env(user=user.id, context=ctx)[model]


def _refused(fn, *args, match=None, **kw):
    with pytest.raises(REFUSED, match=match), fn.__self__.env.cr.savepoint():
        fn(*args, **kw)


def _deliver(c, xmlid, event_type, record):
    """Hand the record's events of this type to the registered subscription,
    exactly as cron_relay does (savepoint, superuser, the event's company)."""
    sub = c.env.ref("%s.%s" % (MOD, xmlid))
    Outbox = c.env["fix.event.outbox"]
    rows = Outbox.search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", record._name),
            ("aggregate_id", "=", record.id),
        ],
        order="id",
    )
    assert rows, "no %s event for %s" % (event_type, record.display_name)
    for row in rows:
        error = Outbox._relay_deliver(sub, row)
        assert error == "", error
    return rows


# ------------------------------------------------------------------ wiring
def test_every_handoff_consumer_is_registered_and_callable(c):
    for xmlid, (event_type, model) in CONSUMERS.items():
        sub = c.env.ref("%s.%s" % (MOD, xmlid))
        assert sub.active and sub.event_type == event_type and sub.model == model
        assert sub.method.startswith("consume_")
        assert callable(getattr(c.env[model], sub.method, None)), sub.method
    # the D8 probes: device events (m17_71) have a consumer
    n = c.env["fix.event.consumer"].search_count(
        [
            (
                "event_type",
                "in",
                ("device.registered", "device.transferred", "device.warranty_updated"),
            )
        ]
    )
    assert n >= 2


# ------------------------------------------------------------------ M49 assets
def test_equipment_registration_raises_one_capitalisation_request(c):
    eq = c.env["fix.equipment"].create(
        {
            "code": "A7BRG-EQ1",
            "name": "Bridge Oscilloscope",
            "company_id": c.co.id,
            "operating_unit_id": c.ou.id,
            "acquisition_cost": 85000.0,
        }
    )
    Req = c.env["fix.asset.finance.request"]
    req = Req.search([("source_model", "=", "fix.equipment"), ("source_res_id", "=", eq.id)])
    assert len(req) == 1 and req.kind == "capitalise" and req.state == "pending"
    assert (req.source_amount, req.amount, req.company_id) == (85000.0, 85000.0, c.co)
    # a cost correction refreshes the pending request, never a second one
    eq.write({"acquisition_cost": 90000.0})
    req.invalidate_recordset()
    assert Req.search_count([("key", "=", req.key)]) == 1 and req.amount == 90000.0
    # a plain user neither sees nor decides it
    _refused(_as(c, c.clerk, "fix.asset.finance.request").browse(req.id).action_accept)
    # the accountant: a category first, then a DRAFT asset, nothing posted
    item = _cost_item(c, 90000.0)
    moves_before = c.env["account.move"].search_count([("company_id", "=", c.co.id)])
    mine = _as(c, c.acct, "fix.asset.finance.request").browse(req.id)
    _refused(mine.action_accept, match="category")
    mine.write({"category_id": c.category.id, "acquisition_line_id": item.id})
    mine.action_accept()
    assert req.state == "accepted" and req.decided_by_id == c.acct
    asset = req.fixed_asset_id
    assert asset.state == "draft" and asset.gross == 90000.0 and asset.company_id == c.co
    assert eq.fixed_asset_id == asset
    assert c.env["account.move"].search_count([("company_id", "=", c.co.id)]) == moves_before
    # the decision is pinned and the link is the bridge's
    _refused(mine.write, {"amount": 1.0})
    _refused(mine.action_reject, "changed my mind")
    _refused(eq.with_user(c.fm).write, {"fixed_asset_id": False})


def test_equipment_write_off_raises_a_draft_disposal_through_m49(c):
    eq = c.env["fix.equipment"].create(
        {
            "code": "A7BRG-EQ2",
            "name": "Bridge Thermal Camera",
            "company_id": c.co.id,
            "operating_unit_id": c.ou.id,
            "acquisition_cost": 40000.0,
        }
    )
    cap = c.env["fix.asset.finance.request"].search([("source_res_id", "=", eq.id)])
    acct_req = _as(c, c.acct, "fix.asset.finance.request")
    acct_req.browse(cap.id).write(
        {"category_id": c.category.id, "acquisition_line_id": _cost_item(c, 40000.0).id}
    )
    acct_req.browse(cap.id).action_accept()
    _as(c, c.acct, "fix.fixed.asset").browse(cap.fixed_asset_id.id).action_activate()
    # M45's approved write-off event (contract payload)
    payload = {
        "equipment": eq.code,
        "approver": "QM",
        "approver_id": c.env.uid,
        "value": 40000.0,
        "basis": "dropped, beyond repair",
        "was_missing": False,
    }
    publish(c.env, "equipment.written_off", "fix.equipment", eq.id, payload)
    _deliver(c, "consumer_equipment_written_off", "equipment.written_off", eq)
    _deliver(c, "consumer_equipment_written_off", "equipment.written_off", eq)  # redelivery
    disp = c.env["fix.asset.finance.request"].search(
        [("source_res_id", "=", eq.id), ("kind", "=", "dispose")]
    )
    assert len(disp) == 1 and disp.fixed_asset_id == cap.fixed_asset_id
    assert disp.disposal_kind == "scrap" and "beyond repair" in disp.basis
    moves_before = c.env["account.move"].search_count([("company_id", "=", c.co.id)])
    acct_req.browse(disp.id).action_accept()
    assert disp.disposal_id.state == "draft" and disp.disposal_id.kind == "scrap"
    assert disp.disposal_id.requested_by_id == c.acct  # M49 SoD: another person approves
    assert disp.fixed_asset_id.state == "active"  # derecognised only when M49 posts
    assert c.env["account.move"].search_count([("company_id", "=", c.co.id)]) == moves_before


def test_vehicle_acquisition_and_archive_reach_m49_once(c):
    brand = c.env["fleet.vehicle.model.brand"].create({"name": "A7BRG Brand"})
    model = c.env["fleet.vehicle.model"].create({"name": "A7BRG Van", "brand_id": brand.id})
    van = c.env["fleet.vehicle"].create(
        {
            "model_id": model.id,
            "license_plate": "A7BRG-11-0001",
            "company_id": c.co.id,
            "net_car_value": 2500000.0,
        }
    )
    Req = c.env["fix.asset.finance.request"]
    cap = Req.search([("source_model", "=", "fleet.vehicle"), ("source_res_id", "=", van.id)])
    assert len(cap) == 1 and cap.kind == "capitalise" and cap.source_amount == 2500000.0
    van.write({"active": False})
    domain = [
        ("source_model", "=", "fleet.vehicle"),
        ("source_res_id", "=", van.id),
        ("kind", "=", "dispose"),
    ]
    assert not Req.search(domain)  # D10: archiving never raises a disposal
    van.write({"active": True, "write_off_date": c.today})
    assert not Req.search(domain)  # nor a cancelled plate: only an M46 Vehicle Disposal
    # a request raised for a vehicle M49 does not hold: finance rejects it with a reason
    disp = Req._m49_dispose_vehicle(van, "test disposal")
    assert len(disp) == 1
    mine = _as(c, c.acct, "fix.asset.finance.request").browse(disp.id)
    mine.write({"disposal_kind": "sale"})
    _refused(mine.action_accept, match="M49 asset")
    _refused(mine.action_reject)
    mine.action_reject("never capitalised in M49: bought before the register")
    assert disp.state == "rejected"


def test_site_asset_registration_and_retirement_reach_m49(c):
    gen = c.env["fix.site.asset"].create(
        {"site_id": c.site.id, "asset_type": "generator", "value": 1000.0}
    )
    Req = c.env["fix.asset.finance.request"]
    assert (
        Req.search_count([("source_model", "=", "fix.site.asset"), ("source_res_id", "=", gen.id)])
        == 1
    )
    # the retirement's DOFA approval (the M63 engine's result; tested in cd_facility)
    gen.sudo()._guarded().write(
        {"dofa_approved": True, "dofa_approved_tier": "tier_5", "dofa_approved_amount": 1000.0}
    )
    gen.action_retire(reason="burnt out")
    disp = Req.search(
        [
            ("source_model", "=", "fix.site.asset"),
            ("source_res_id", "=", gen.id),
            ("kind", "=", "dispose"),
        ]
    )
    assert len(disp) == 1 and "burnt out" in disp.basis and disp.operating_unit_id == c.ou


# ------------------------------------------------------------------ M19/M49 IFRS 16
def _site_lease(c, **kw):
    vals = {
        "site_id": c.site.id,
        "lessor_id": c.landlord.id,
        "start_date": c.today.replace(day=1),
        "end_date": c.today.replace(day=1) + timedelta(days=3 * 365),
        "monthly_rent": 120000.0,
        "escalation_pct": 5.0,
        "deposit": 720000.0,
    }
    vals.update(kw)
    # D6 (S4): a lease a person records awaits its DOFA approval; one recorded by
    # trusted code (the migration of signed leases) is active, as these tests need
    return c.env["fix.site.lease"].sudo().create(vals)


def test_recorded_lease_becomes_one_draft_ifrs16_contract(c):
    ls = _site_lease(c)
    _deliver(c, "consumer_lease_recorded", "lease.recorded", ls)
    _deliver(c, "consumer_lease_extract_published", "lease.extract_published", ls)
    _deliver(c, "consumer_lease_recorded", "lease.recorded", ls)  # redelivery
    lease = c.env["fix.lease"].search([("site_lease_id", "=", ls.id)])
    assert len(lease) == 1 and lease.state == "draft"
    assert lease.payment_amount == 120000.0 and lease.partner_id == c.landlord
    assert lease.commencement_date == ls.start_date and lease.term_months >= 36
    assert lease.site_extract_version == 1 and lease.site_escalation_pct == 5.0
    assert lease.ibr_percent == 0.0 and lease.company_id == c.co
    assert ls.extract_ids.consumed_by_m19_at
    # finance cannot commence it on a 0% rate (the undiscounted rent as liability)
    _refused(_as(c, c.acct, "fix.lease").browse(lease.id).action_activate, match="borrowing rate")
    # the link is the bridge's
    _refused(_as(c, c.acct, "fix.lease").browse(lease.id).write, {"site_lease_id": False})


def test_later_extract_updates_the_draft_then_raises_a_modification_item(c):
    ls = _site_lease(c)
    _deliver(c, "consumer_lease_extract_published", "lease.extract_published", ls)
    lease = c.env["fix.lease"].search([("site_lease_id", "=", ls.id)])
    # v2 while draft: the draft follows (the modification's own service write)
    ls.sudo()._guarded().write({"monthly_rent": 130000.0})
    ls.sudo()._lease_publish_extract("modified")
    _deliver(c, "consumer_lease_extract_published", "lease.extract_published", ls)
    assert lease.payment_amount == 130000.0 and lease.site_extract_version == 2
    assert not lease.modification_item_ids
    # commenced (as M49 Activate leaves it) -> v3 changes nothing in the book
    lease.sudo().write({"state": "active"})
    ls.sudo()._guarded().write({"monthly_rent": 150000.0})
    ls.sudo()._lease_publish_extract("modified")
    _deliver(c, "consumer_lease_extract_published", "lease.extract_published", ls)
    _deliver(c, "consumer_lease_extract_published", "lease.extract_published", ls)
    assert lease.payment_amount == 130000.0
    item = lease.modification_item_ids
    assert len(item) == 1 and item.version == 3 and item.state == "open"
    assert "150000" in item.changes
    _refused(
        _as(c, c.clerk, "fix.lease.modification.item").browse(item.id).action_mark_remeasured, "x"
    )
    mine = _as(c, c.acct, "fix.lease.modification.item").browse(item.id)
    _refused(mine.action_mark_remeasured)
    # A07 FIN-07: "remeasured" is a posted remeasurement, never a tick
    _refused(mine.action_mark_remeasured, "remeasured by hand", match="remeasurement")
    _refused(mine.action_mark_no_change)
    mine.action_mark_no_change("rent change handled on the replacement contract")
    assert item.state == "no_change" and item.decided_by_id == c.acct


def test_lease_with_no_rent_waits_as_an_exception_not_a_fabricated_contract(c):
    ls = _site_lease(c, monthly_rent=0.0)
    _deliver(c, "consumer_lease_recorded", "lease.recorded", ls)
    assert not c.env["fix.lease"].search([("site_lease_id", "=", ls.id)])
    exc = c.env["fix.bridge.exception"].search([("key", "=", "m49_lease:%s" % ls.id)])
    assert exc.state == "open" and "no monthly rent" in exc.message
    # once M47 corrects the rent, Retry drafts it and resolves the exception
    ls.sudo()._guarded().write({"monthly_rent": 90000.0})
    _as(c, c.acct, "fix.bridge.exception").browse(exc.id).action_retry()
    assert c.env["fix.lease"].search([("site_lease_id", "=", ls.id)]).payment_amount == 90000.0
    assert exc.state == "resolved"


# ------------------------------------------------------------------ M52 cost
def _work_order(c):
    return c.env["fix.facility.work.order"].create(
        {"site_id": c.site.id, "description": "Generator overhaul", "company_id": c.co.id}
    )


def _wo_closed(c, wo, cost, vendor=None, ref="INV-77"):
    publish(
        c.env,
        "facility.work_order_closed",
        "fix.facility.work.order",
        wo.id,
        {
            "order": wo.name,
            "site": c.site.name,
            "site_id": c.site.id,
            "company_id": c.co.id,
            "work_type": "corrective",
            "assigned_type": "vendor",
            "vendor_id": (vendor or c.vendor).id,
            "vendor": (vendor or c.vendor).name,
            "cost": cost,
            "estimated_cost": cost,
            "currency": "BDT",
            "invoice_ref": ref,
            "verified_by": "FM",
            "completed_at": fields.Datetime.to_string(fields.Datetime.now()),
            "verified_at": fields.Datetime.to_string(fields.Datetime.now()),
        },
    )


def _bill(c, vendor, gross):
    product = c.env["product.product"].create({"name": "A7BRG service", "type": "service"})
    return c.env["fix.vendor.invoice"].create(
        {
            "company_id": c.co.id,
            "operating_unit_id": c.ou.id,
            "vendor_id": vendor.id,
            "invoice_ref": "INV-77",
            "bill_type": "non_po",
            "line_ids": [
                (0, 0, {"product_id": product.id, "description": "overhaul", "unit_price": gross})
            ],
        }
    )


def _repair_account(c):
    account = c.env["account.account"].create(
        {
            "code": "A7R%s" % c.co.id,
            "name": "A07 Repair & Maintenance",
            "account_type": "expense",
            "company_ids": [(6, 0, c.co.ids)],
        }
    )
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_asset_finance_hse_bridge.account.facility_work_order", "A7R%s" % c.co.id
    )
    return account


def test_closed_work_order_becomes_one_pending_cost_entry_matched_to_its_bill(c):
    _repair_account(c)
    wo = _work_order(c)
    _wo_closed(c, wo, 45000.0)
    _deliver(c, "consumer_facility_work_order_closed", "facility.work_order_closed", wo)
    _deliver(c, "consumer_facility_work_order_closed", "facility.work_order_closed", wo)
    Entry = c.env["fix.asset.cost.entry"]
    entry = Entry.search([("source_model", "=", wo._name), ("source_res_id", "=", wo.id)])
    assert len(entry) == 1 and entry.state == "pending" and entry.amount == 45000.0
    assert entry.vendor_id == c.vendor and entry.invoice_ref == "INV-77"
    assert entry.operating_unit_id == c.ou and entry.company_id == c.co
    # reopened and re-closed at another cost: the pending entry follows, still one
    _wo_closed(c, wo, 47000.0)
    _deliver(c, "consumer_facility_work_order_closed", "facility.work_order_closed", wo)
    assert Entry.search_count([("key", "=", entry.key)]) == 1 and entry.amount == 47000.0
    # the figures are the source's
    mine = _as(c, c.acct, "fix.asset.cost.entry").browse(entry.id)
    _refused(mine.write, {"amount": 1.0})
    other = c.env["res.partner"].create({"name": "A7BRG Other Vendor"})
    _refused(mine.action_match_bill, _bill(c, other, 47000.0).id, match="vendor")
    small = _bill(c, c.vendor, 1000.0)
    _refused(mine.action_match_bill, small.id, match="above the")
    _refused(_as(c, c.clerk, "fix.asset.cost.entry").browse(entry.id).action_match_bill, small.id)
    bill = _bill(c, c.vendor, 47000.0)
    mine.action_match_bill(bill.id)
    assert entry.state == "matched" and entry.vendor_invoice_id == bill
    # a re-close after the decision flags it for AP instead of rewriting it
    _wo_closed(c, wo, 52000.0)
    _deliver(c, "consumer_facility_work_order_closed", "facility.work_order_closed", wo)
    assert entry.amount == 47000.0 and entry.source_changed


def test_fuel_and_service_costs_become_pending_entries_by_branch(c):
    brand = c.env["fleet.vehicle.model.brand"].create({"name": "A7BRG Brand2"})
    model = c.env["fleet.vehicle.model"].create({"name": "A7BRG Bike", "brand_id": brand.id})
    van = c.env["fleet.vehicle"].create(
        {
            "model_id": model.id,
            "license_plate": "A7BRG-11-0003",
            "company_id": c.co.id,
            "operating_unit_id": c.ou.id,
        }
    )
    fuel = (
        c.env["fix.vehicle.fuel"]
        .sudo()
        .create(
            {
                "vehicle_id": van.id,
                "litres": 3.0,
                "odometer": 100,
                "amount": 400.0,
                "receipt_no": "R-9",
            }
        )
    )
    pm = c.env["fix.vehicle.pm"].sudo().create({"vehicle_id": van.id, "cost": 2200.0})
    publish(
        c.env,
        "vehicle.fuel_recorded",
        "fix.vehicle.fuel",
        fuel.id,
        {
            "vehicle": van.license_plate,
            "vehicle_id": van.id,
            "fuel": fuel.name,
            "driver_id": False,
            "filled_on": str(c.today),
            "litres": 3.0,
            "amount": 400.0,
            "odometer": 100,
            "receipt_no": "R-9",
        },
    )
    publish(
        c.env,
        "vehicle.service_completed",
        "fix.vehicle.pm",
        pm.id,
        {
            "vehicle": van.license_plate,
            "vehicle_id": van.id,
            "pm": pm.name,
            "pm_type": "service",
            "odometer": 100,
            "cost": 2200.0,
            "done_on": str(c.today),
        },
    )
    _deliver(c, "consumer_vehicle_fuel_recorded", "vehicle.fuel_recorded", fuel)
    _deliver(c, "consumer_vehicle_service_completed", "vehicle.service_completed", pm)
    _deliver(c, "consumer_vehicle_fuel_recorded", "vehicle.fuel_recorded", fuel)
    entries = c.env["fix.asset.cost.entry"].search([("vehicle_id", "=", van.id)])
    assert sorted(entries.mapped("cost_type")) == ["vehicle_fuel", "vehicle_service"]
    assert entries.mapped("operating_unit_id") == c.ou
    assert sorted(entries.mapped("amount")) == [400.0, 2200.0]
    fuel_entry = entries.filtered(lambda e: e.cost_type == "vehicle_fuel")
    assert fuel_entry.invoice_ref == "R-9" and not fuel_entry.vendor_id
    mine = _as(c, c.acct, "fix.asset.cost.entry").browse(fuel_entry.id)
    _refused(mine.action_reject)
    mine.action_reject("paid from the branch petty cash float")
    assert fuel_entry.state == "rejected"


# ------------------------------------------------------------------ M59 HSE
def test_site_injury_opens_one_hse_case_with_the_clock_and_writes_the_ref_back(c):
    inc = (
        c.env["fix.site.incident"]
        .with_user(c.fm)
        .create(
            {
                "site_id": c.site.id,
                "incident_type": "injury",
                "severity": "medium",
                "description": "Technician cut by a fan blade",
            }
        )
    )
    assert inc.hse_notice_due_on
    _deliver(c, "consumer_site_incident", "site.incident", inc)
    _deliver(c, "consumer_site_incident", "site.incident", inc)
    case = c.env["fix.hse.incident"].search([("site_incident_id", "=", inc.id)])
    assert len(case) == 1 and case.state == "reported" and case.incident_type == "injury"
    assert case.severity == "medium" and case.company_id == c.co
    assert case.notice_due and case.notice_form == "form_27"
    assert case.statutory_record_id  # BLA s.90 register for a medium injury
    assert case.employee_id.user_id == c.fm  # the reporter
    assert case.source_notice_due_on == inc.hse_notice_due_on
    assert fields.Datetime.to_datetime(case.notice_due).date() >= inc.hse_notice_due_on
    assert inc.hse_case_ref == case.name
    _refused(_as(c, c.hse, "fix.hse.incident").browse(case.id).write, {"bridge_source_key": "x"})


def test_injury_without_a_named_worker_waits_for_the_hse_officer(c):
    inc = c.env["fix.site.incident"].create(  # superuser: no employee behind the reporter
        {
            "site_id": c.site.id,
            "incident_type": "fire",
            "injuries_flag": True,
            "severity": "high",
            "description": "Battery fire, one burn",
        }
    )
    _deliver(c, "consumer_site_incident", "site.incident", inc)
    assert not c.env["fix.hse.incident"].search([("site_incident_id", "=", inc.id)])
    exc = c.env["fix.bridge.exception"].search([("key", "=", "m59:fix.site.incident:%s" % inc.id)])
    assert exc.state == "open" and exc.route == "m59_case" and "name the worker" in exc.message
    # a plain user cannot retry it; the HSE officer names the worker and retries
    _refused(_as(c, c.clerk, "fix.bridge.exception").browse(exc.id).action_retry)
    worker = c.env["hr.employee"].create({"name": "A7BRG Injured Tech", "company_id": c.co.id})
    mine = _as(c, c.hse, "fix.bridge.exception").browse(exc.id)
    mine.write({"employee_id": worker.id})
    mine.action_retry()
    case = c.env["fix.hse.incident"].search([("site_incident_id", "=", inc.id)])
    assert case.employee_id == worker and case.severity == "high" and inc.hse_case_ref == case.name
    assert exc.state == "resolved"
    _refused(mine.write, {"message": "nothing to see"})


def test_injury_ticked_later_and_vehicle_accident_open_cases(c):
    inc = (
        c.env["fix.site.incident"]
        .with_user(c.fm)
        .create({"site_id": c.site.id, "incident_type": "theft", "description": "Break-in"})
    )
    _deliver(c, "consumer_site_incident", "site.incident", inc)
    assert not c.env["fix.hse.incident"].search([("site_incident_id", "=", inc.id)])
    inc.with_user(c.fm).write({"injuries_flag": True})  # the guard was hurt
    case = c.env["fix.hse.incident"].search([("site_incident_id", "=", inc.id)])
    assert len(case) == 1 and inc.hse_case_ref == case.name
    # M46 accident with injuries, reported by someone with an employee record
    brand = c.env["fleet.vehicle.model.brand"].create({"name": "A7BRG Brand3"})
    model = c.env["fleet.vehicle.model"].create({"name": "A7BRG Car", "brand_id": brand.id})
    van = c.env["fleet.vehicle"].create(
        {"model_id": model.id, "license_plate": "A7BRG-11-0004", "company_id": c.co.id}
    )
    acc = c.env["fix.vehicle.accident"].create(
        {"vehicle_id": van.id, "description": "Rear-ended at a signal", "injury": True}
    )
    acc_case_key = "m59:fix.vehicle.accident:%s" % acc.id
    _deliver(c, "consumer_vehicle_incident", "vehicle.incident", acc)
    # superuser reporter: no worker -> waits (medium is the fail-safe default severity)
    exc = c.env["fix.bridge.exception"].search([("key", "=", acc_case_key)])
    assert exc.state == "open" and "medium severity" in exc.message
    worker = c.env["hr.employee"].create({"name": "A7BRG Driver", "company_id": c.co.id})
    exc.sudo().write({"employee_id": worker.id})
    _as(c, c.hse, "fix.bridge.exception").browse(exc.id).action_retry()
    case = c.env["fix.hse.incident"].search([("vehicle_accident_id", "=", acc.id)])
    assert case.severity == "medium" and acc.hse_case_ref == case.name


def test_unfit_safety_equipment_raises_one_open_hazard_per_item(c):
    item = (
        c.env["fix.site.safety"]
        .sudo()
        .create(
            {
                "site_id": c.site.id,
                "equipment_type": "extinguisher",
                "ref": "EXT-7",
                "next_check": c.today - timedelta(days=2),
            }
        )
    )
    c.env["fix.site.safety"].cron_safety_due()
    _deliver(c, "consumer_site_safety_equipment_unfit", "site.safety_equipment_unfit", item)
    _deliver(c, "consumer_site_safety_equipment_unfit", "site.safety_equipment_unfit", item)
    Hazard = c.env["fix.hse.hazard"]
    hazard = Hazard.search([("site_safety_id", "=", item.id)])
    assert len(hazard) == 1 and hazard.state == "open" and "EXT-7" in hazard.name
    assert hazard.company_id == c.co and hazard.operating_unit_id == c.ou
    # closed by HSE -> the next lapse opens a new one. A09 M62 (merged): a
    # hazard is scored and controlled first, then closed by a second officer.
    hazard.sudo().write(
        {
            "controls": "Extinguisher replaced; monthly checks rescheduled.",
            "residual_likelihood": 1,
            "residual_severity": 1,
        }
    )
    hazard.with_user(c.hse).action_control()
    hazard.with_user(c.hse2).action_close()
    item.sudo()._guarded().write({"next_check": c.today - timedelta(days=1)})
    c.env["fix.site.safety"].cron_safety_due()
    _deliver(c, "consumer_site_safety_equipment_unfit", "site.safety_equipment_unfit", item)
    assert Hazard.search_count([("site_safety_id", "=", item.id)]) == 2
    assert Hazard.search_count([("site_safety_id", "=", item.id), ("state", "=", "open")]) == 1


# ------------------------------------------------------------------ M60 risk
def test_lapses_raise_or_update_one_open_risk_per_subject(c):
    emp = c.env["hr.employee"].create({"name": "A7BRG Driver2", "company_id": c.co.id})
    driver = (
        c.env["fix.driver"]
        .sudo()
        .create({"name": "A7BRG Driver2", "employee_id": emp.id, "license_no": "DL-A7-1"})
    )
    for expiry in ("2026-10-01", "2026-11-01"):
        publish(
            c.env,
            "driver.licence_expired",
            "fix.driver",
            driver.id,
            {
                "driver": driver.name,
                "driver_id": driver.id,
                "employee_id": emp.id,
                "licence_class": "Light",
                "expiry_date": expiry,
            },
        )
    _deliver(c, "consumer_driver_licence_expired", "driver.licence_expired", driver)
    _deliver(c, "consumer_driver_licence_expired", "driver.licence_expired", driver)
    Risk = c.env["fix.risk.register"]
    risk = Risk.search([("bridge_subject_key", "=", "m60:fix.driver:%s" % driver.id)])
    assert len(risk) == 1 and risk.state == "open" and risk.category == "compliance"
    assert risk.bridge_trigger_count == 2 and "2026-11-01" in risk.bridge_lapse_log
    # site: the licence lapse and the operating-risk exception share the site's entry
    licence_payload = {
        "site": c.site.name,
        "site_id": c.site.id,
        "licence": "Trade Licence",
        "licence_type": "trade",
        "expiry": "2026-10-31",
    }
    licence = (
        c.env["fix.site.licence"]
        .sudo()
        .create(
            {
                "site_id": c.site.id,
                "name": "Trade Licence",
                "licence_type": "trade",
                "valid_to": c.today + timedelta(days=30),
            }
        )
    )
    publish(c.env, "site.compliance_expired", "fix.site.licence", licence.id, licence_payload)
    _deliver(c, "consumer_site_compliance_expired", "site.compliance_expired", licence)
    exc = (
        c.env["fix.site.risk.exception"]
        .sudo()
        ._guarded()
        .create({"name": "SRISK/T", "site_id": c.site.id, "severity": "critical"})
    )
    publish(
        c.env,
        "site.risk_exception_raised",
        "fix.site.risk.exception",
        exc.id,
        {
            "exception": exc.name,
            "site": c.site.name,
            "site_id": c.site.id,
            "licence": "Trade Licence",
            "licence_type": "trade",
            "expiry": "2026-10-31",
            "severity": "critical",
            "decision_required": True,
        },
    )
    _deliver(c, "consumer_site_risk_exception_raised", "site.risk_exception_raised", exc)
    site_risk = Risk.search([("bridge_subject_key", "=", "m60:fix.site:%s" % c.site.id)])
    assert len(site_risk) == 1 and site_risk.company_id == c.co
    assert site_risk.bridge_trigger_count == 2 and "SRISK/T" in site_risk.bridge_lapse_log
    # the decision lands on the same entry, which stays open for the risk owner
    publish(
        c.env,
        "site.risk_decision_recorded",
        "fix.site.risk.exception",
        exc.id,
        {
            "exception": exc.name,
            "site": c.site.name,
            "site_id": c.site.id,
            "decision": "continue",
            "decided_by": "COO",
            "review_due_on": str(c.today + timedelta(days=7)),
        },
    )
    _deliver(c, "consumer_site_risk_decision_recorded", "site.risk_decision_recorded", exc)
    assert "continue" in site_risk.bridge_lapse_log and site_risk.state == "open"
    # a user cannot unhook an entry from its subject (that would allow a duplicate)
    _refused(Risk.with_user(c.clerk).browse(site_risk.id).write, {"bridge_subject_key": False})
    # closed by the risk owner -> the next lapse opens a new entry
    risk.write({"state": "closed"})
    publish(
        c.env,
        "driver.licence_expired",
        "fix.driver",
        driver.id,
        {
            "driver": driver.name,
            "driver_id": driver.id,
            "employee_id": emp.id,
            "licence_class": "Light",
            "expiry_date": "2027-01-01",
        },
    )
    _deliver(c, "consumer_driver_licence_expired", "driver.licence_expired", driver)
    keyed = Risk.search([("bridge_subject_key", "=", "m60:fix.driver:%s" % driver.id)])
    assert len(keyed) == 2 and len(keyed.filtered(lambda r: r.state != "closed")) == 1


def test_vehicle_document_lapse_raises_one_risk_per_vehicle(c):
    brand = c.env["fleet.vehicle.model.brand"].create({"name": "A7BRG Brand4"})
    model = c.env["fleet.vehicle.model"].create({"name": "A7BRG Truck", "brand_id": brand.id})
    van = c.env["fleet.vehicle"].create(
        {"model_id": model.id, "license_plate": "A7BRG-11-0005", "company_id": c.co.id}
    )
    docs = (
        c.env["fix.vehicle.document"]
        .sudo()
        .create(
            [
                {
                    "vehicle_id": van.id,
                    "doc_type": "insurance",
                    "valid_to": c.today - timedelta(days=1),
                },
                {
                    "vehicle_id": van.id,
                    "doc_type": "fitness",
                    "valid_to": c.today - timedelta(days=1),
                },
            ]
        )
    )
    for doc in docs:
        publish(
            c.env,
            "vehicle.document_expired",
            "fix.vehicle.document",
            doc.id,
            {
                "vehicle": van.license_plate,
                "vehicle_id": van.id,
                "document": doc.name,
                "doc_type": doc.doc_type,
                "expiry_date": str(doc.valid_to),
            },
        )
        _deliver(c, "consumer_vehicle_document_expired", "vehicle.document_expired", doc)
    risk = c.env["fix.risk.register"].search(
        [("bridge_subject_key", "=", "m60:fleet.vehicle:%s" % van.id)]
    )
    assert len(risk) == 1 and risk.bridge_trigger_count == 2


# ------------------------------------------------------------------ M09 claims
@pytest.fixture
def claim(c):
    env = c.env
    ou = c.ou
    entity = env["fix.entity"].create(
        {"code": "A7BRGE", "legal_name": "A7 Bridge Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "A7 Bridge Desk",
            "code": "A7BD",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "A7BrgBrand", "code": "A7BB"})
    model = env["fix.device.model"].create({"name": "A7BrgPhone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "A7 Bridge Customer"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-A7BRG-1"}
    )
    env["fix.warranty"].create(
        {
            "device_id": device.id,
            "start_date": c.today - timedelta(days=60),
            "end_date": c.today + timedelta(days=300),
            "status": "active",
        }
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "Speaker dead",
            "order_category": "warranty",
        }
    )
    rec = env["fix.warranty.claim"].create(
        {
            "company_id": c.co.id,
            "operating_unit_id": ou.id,
            "service_order_id": order.id,
            "brand_id": brand.id,
            "claim_amount": 5000.0,
        }
    )
    return types.SimpleNamespace(claim=rec, device=device, customer=customer)


def test_device_owner_or_warranty_change_puts_open_claims_on_recheck(c, claim):
    new_owner = c.env["res.partner"].create({"name": "A7 Bridge Second Owner"})
    claim.device.write({"owner_id": new_owner.id})
    _deliver(c, "consumer_device_transferred", "device.transferred", claim.device)
    _deliver(c, "consumer_device_transferred", "device.transferred", claim.device)
    cl = claim.claim
    assert cl.device_recheck_required and cl.device_recheck_reason.count("owner changed") == 1
    # submission waits for the re-check (before the evidence gate is even read)
    _refused(cl.with_user(c.clerk).action_submit, match="device changed")
    _refused(cl.with_user(c.clerk).write, {"device_recheck_required": False})
    _refused(cl.with_user(c.clerk).action_confirm_device_recheck)
    cl.with_user(c.clerk).action_confirm_device_recheck("new owner's purchase proof attached")
    assert not cl.device_recheck_required and cl.device_recheck_confirmed_by_id == c.clerk
    # the claim is back under M09's own gate (the evidence pack)
    _refused(cl.with_user(c.clerk).action_submit, match="missing evidence")
    # a warranty change flags it again
    claim.device.write(
        {
            "warranty_id": [
                (
                    0,
                    0,
                    {
                        "start_date": c.today - timedelta(days=10),
                        "end_date": c.today + timedelta(days=355),
                        "status": "active",
                    },
                )
            ]
        }
    )
    _deliver(c, "consumer_device_warranty_updated", "device.warranty_updated", claim.device)
    assert cl.device_recheck_required and "warranty changed" in cl.device_recheck_reason


def test_outbox_payloads_used_here_match_the_contracts(c):
    """The consumers read only keys the event contracts declare."""
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[5] / "contracts" / "events"
    reads = {
        "equipment.written_off": {"value", "basis", "approver", "was_missing"},
        "lease.extract_published": {"version", "extract", "reason"},
        "facility.work_order_closed": {
            "cost",
            "company_id",
            "vendor_id",
            "invoice_ref",
            "verified_at",
            "work_type",
            "assigned_type",
        },
        "vehicle.fuel_recorded": {"amount", "filled_on", "receipt_no", "litres"},
        "vehicle.service_completed": {"cost", "done_on", "pm_type", "odometer"},
        "site.incident": {"injuries_flag"},
        "vehicle.incident": {"injuries"},
        "site.safety_equipment_unfit": {"due_date"},
        "site.risk_exception_raised": {"licence", "licence_type", "expiry", "severity"},
        "site.risk_decision_recorded": {"decision", "decided_by", "review_due_on"},
        "site.compliance_expired": {"licence", "licence_type", "expiry"},
        "driver.licence_expired": {"licence_class", "expiry_date"},
        "vehicle.document_expired": {"doc_type", "document", "expiry_date"},
    }
    for event_type, keys in reads.items():
        contract = json.loads((root / (event_type.replace(".", "_") + ".json")).read_text())
        declared = set(contract["properties"]["payload"]["properties"])
        assert keys <= declared, (event_type, keys - declared)


def test_a_failing_hand_off_never_undoes_the_users_change(c, monkeypatch):
    """The register write commits; the hand-off failure becomes an open exception."""
    Req = type(c.env["fix.asset.finance.request"])

    def boom(self, records):
        raise UserError("M49 is down")

    monkeypatch.setattr(Req, "_m49_capitalise_equipment", boom)
    eq = c.env["fix.equipment"].create(
        {
            "code": "A7BRG-EQ3",
            "name": "Bridge Megger",
            "company_id": c.co.id,
            "acquisition_cost": 12000.0,
        }
    )
    assert eq.exists() and eq.acquisition_cost == 12000.0
    exc = c.env["fix.bridge.exception"].search(
        [("source_model", "=", "fix.equipment"), ("source_res_id", "=", eq.id)]
    )
    assert exc.state == "open" and "M49 is down" in exc.message
    assert not c.env["fix.asset.finance.request"].search(
        [("source_res_id", "=", eq.id), ("source_model", "=", "fix.equipment")]
    )
