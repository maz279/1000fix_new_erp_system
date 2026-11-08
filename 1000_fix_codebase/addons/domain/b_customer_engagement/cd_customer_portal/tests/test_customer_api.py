"""Behavioural tests for the P01 customer self-service API (live ORM).

``odoo_env`` (database fix_test, rolled back per test) with ``odoo.http.request``
replaced by a minimal stand-in exposing ``env`` / ``session`` - the controller
code itself runs unmodified. Security of the public routes lives in
test_api_security.py; this file covers the authenticated customer journeys.
"""

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo import Command, http
from odoo.addons.cd_customer_portal.controllers import customer_api
from odoo.addons.cd_customer_portal.controllers.customer_api import CustomerApiController
from odoo.exceptions import UserError


class _Browser:
    def __init__(self, env, user):
        self.env = env(user=user.id)
        self.session = http.Session(http.get_default_session(), f"sid-{id(self)}", new=True)


@contextmanager
def _as(world, user):
    with patch.object(customer_api, "request", _Browser(world.env, user)):
        yield CustomerApiController()


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    # fix.entity is UNIQUE per company: a dedicated company keeps this fixture
    # from queueing behind other suites' entity on the shared test database
    company = env["res.company"].create({"name": "Customer Portal Test Co"})
    entity = env["fix.entity"].create(
        {"code": "CPENT", "legal_name": "Customer Portal Entity", "company_id": company.id}
    )
    branch = env["fix.branch"].create(
        {"name": "CP Dhanmondi", "code": "CPDH", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "CPBrand", "code": "CPBR"})
    phone_model = env["fix.device.model"].create(
        {"name": "CP Phone X", "brand_id": brand.id, "device_type": "smartphone"}
    )
    portal = env.ref("base.group_portal")
    users = env["res.users"].with_context(no_reset_password=True)
    alice = users.create(
        {"name": "Alice CP", "login": "alice@cp.test", "group_ids": [Command.set([portal.id])]}
    )
    bob = users.create(
        {"name": "Bob CP", "login": "bob@cp.test", "group_ids": [Command.set([portal.id])]}
    )
    staff = users.create({"name": "Staff CP", "login": "staff@cp.test"})
    device = env["fix.device"].create(
        {
            "device_model_id": phone_model.id,
            "owner_id": alice.partner_id.id,
            "serial_number": "SN-CP-ALICE-1",
            "branch_id": branch.id,
        }
    )
    device.add_history("registered", "Registered at CP Dhanmondi")
    return SimpleNamespace(
        env=env,
        branch=branch,
        model=phone_model,
        alice=alice,
        bob=bob,
        staff=staff,
        device=device,
    )


def _order(world, device=None, **vals):
    device = device or world.device
    return world.env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": device.owner_id.id,
            "branch_id": world.branch.id,
            "fault_description": "Screen flicker",
            **vals,
        }
    )


def _estimate(world, order, amount, state="sent"):
    estimate = world.env["fix.estimate"].create({"order_id": order.id})
    if amount:
        world.env["fix.estimate.line"].create(
            {"estimate_id": estimate.id, "description": "Display", "unit_price": amount}
        )
    estimate.state = state
    return estimate


# --- money formatting (BN-007) ------------------------------------------------------


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (0, "0.00"),
        (999.5, "999.50"),
        (1234.5, "1,234.50"),
        (12345678.9, "1,23,45,678.90"),
        (100000, "1,00,000.00"),
        (-1234567.5, "-12,34,567.50"),
        (None, "0.00"),
        ("n/a", "0.00"),
    ],
)
def test_amounts_are_south_asian_grouped(amount, expected):
    assert customer_api._fmt_bdt(amount) == expected


# --- catalogue & branches -----------------------------------------------------------


def test_models_and_branches_feed_the_registration_dropdowns(world):
    with _as(world, world.alice) as ctrl:
        models = ctrl.models()
        branches = ctrl.branches()
    mine = next(m for m in models["models"] if m["id"] == world.model.id)
    assert mine == {
        "id": world.model.id,
        "name": "CP Phone X",
        "brand": "CPBrand",
        "device_type": "smartphone",
    }
    assert models["total"] == len(models["models"])
    assert {"id": world.branch.id, "name": "CP Dhanmondi"} in branches["branches"]


# --- devices ------------------------------------------------------------------------


def test_devices_list_the_customers_registry_with_history(world):
    with _as(world, world.alice) as ctrl:
        res = ctrl.devices()
    [dev] = res["devices"]
    assert dev["id"] == world.device.id
    assert dev["model"] == "CP Phone X"
    assert dev["brand"] == "CPBrand"
    assert dev["identifier"] == "SN-CP-…"
    assert dev["state"] == "registered"
    assert [h["event"] for h in dev["history"]] == ["registered"]
    assert dev["history"][0]["description"] == "Registered at CP Dhanmondi"


def test_register_device_validates_the_model_and_identity(world):
    """Regression: the IMEI constraint raises after the INSERT - the rejected
    device used to stay in the committed request transaction."""
    with _as(world, world.bob) as ctrl:
        missing = ctrl.devices(action="register")
        unknown = ctrl.devices(device_model_id=999999999)
        junk = ctrl.devices(device_model_id="phone")
        anonymous = ctrl.devices(device_model_id=world.model.id, serial_number="  ")
        bad_imei = ctrl.devices(device_model_id=world.model.id, imei_1="123")
        bad_channel = ctrl.devices(
            device_model_id=world.model.id, serial_number="SN-CP-X", purchase_channel="bazaar"
        )
    assert missing["error"]["code"] == "missing_model"
    assert unknown["error"]["code"] == "invalid_model"
    assert junk["error"]["code"] == "invalid_model"
    assert anonymous["error"]["code"] == "missing_identifier"
    assert bad_imei["error"]["code"] == "registration_rejected"
    assert "IMEI" in bad_imei["error"]["message"]
    assert bad_channel["error"]["code"] == "registration_rejected"
    assert not world.env["fix.device"].search([("owner_id", "=", world.bob.partner_id.id)])


def test_register_device_lands_in_the_callers_registry(world):
    with _as(world, world.bob) as ctrl:
        res = ctrl.devices(
            device_model_id=world.model.id,
            imei_1="356938035643809",
            purchase_channel="online",
            partner_id=world.alice.partner_id.id,  # ignored for a portal user
        )
    device = world.env["fix.device"].browse(res["device"]["id"])
    assert res["registered"] is True
    assert res["device"]["identifier"] == "356938…"
    assert device.owner_id == world.bob.partner_id
    assert device.branch_id == world.branch
    assert device.purchase_channel == "online"


def test_register_device_without_any_branch(odoo_env):
    """Fresh install: no branch exists yet - the device registers unassigned."""
    env = odoo_env
    assert not env["fix.branch"].search([])
    brand = env["fix.brand"].create({"name": "CPLoneBrand", "code": "CPLB"})
    model = env["fix.device.model"].create({"name": "CP Lone", "brand_id": brand.id})
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Lone CP",
                "login": "lone@cp.test",
                "group_ids": [Command.set([env.ref("base.group_portal").id])],
            }
        )
    )
    with patch.object(customer_api, "request", _Browser(env, user)):
        res = CustomerApiController().devices(device_model_id=model.id, serial_number="SN-LONE")
    assert res["registered"] is True
    assert not env["fix.device"].browse(res["device"]["id"]).branch_id


# --- ownership transfer -------------------------------------------------------------


def test_ownership_transfer_is_owner_only_and_audited(world):
    device = world.device
    with _as(world, world.bob) as ctrl:
        missing = ctrl.ownership_transfer(device_id=device.id)
        unknown = ctrl.ownership_transfer(device_id="x", to_partner_id=world.bob.partner_id.id)
        thief = ctrl.ownership_transfer(device_id=device.id, to_partner_id=world.bob.partner_id.id)
    with _as(world, world.alice) as ctrl:
        nobody = ctrl.ownership_transfer(device_id=device.id, to_partner_id=999999999)
        done = ctrl.ownership_transfer(device_id=device.id, to_partner_id=world.bob.partner_id.id)
    assert missing["error"]["code"] == "missing_params"
    assert unknown["error"]["code"] == "no_device"
    assert thief["error"]["code"] == "not_owner"
    assert nobody["error"]["code"] == "no_recipient"
    assert done == {"transferred": True, "device_id": device.id}
    assert device.owner_id == world.bob.partner_id
    trail = world.env["fix.device.ownership"].search([("device_id", "=", device.id)])
    assert trail.from_partner_id == world.alice.partner_id
    assert trail.to_partner_id == world.bob.partner_id
    # A07 operability M17-11: the trail says who asked and how, not "data migration"
    assert trail.channel == "customer_portal"
    assert world.alice.partner_id.name in trail.reason


def test_a_portal_transfer_records_the_customers_reason_and_type(world):
    device = world.device
    with _as(world, world.alice) as ctrl:
        unknown = ctrl.ownership_transfer(
            device_id=device.id, to_partner_id=world.bob.partner_id.id, transfer_type="stolen"
        )
        done = ctrl.ownership_transfer(
            device_id=device.id,
            to_partner_id=world.bob.partner_id.id,
            transfer_type="gift",
            reason="Given to my brother",
        )
    assert unknown["error"]["code"] == "invalid_transfer_type"
    assert done["transferred"]
    trail = world.env["fix.device.ownership"].search([("device_id", "=", device.id)])
    assert (trail.transfer_type, trail.reason, trail.channel) == (
        "gift",
        "Given to my brother",
        "customer_portal",
    )


def test_a_rejected_transfer_is_reported(world):
    with (
        patch.object(
            type(world.env["fix.device"]),
            "action_transfer_ownership",
            side_effect=UserError("device is in service"),
        ),
        _as(world, world.alice) as ctrl,
    ):
        res = ctrl.ownership_transfer(
            device_id=world.device.id, to_partner_id=world.bob.partner_id.id
        )
    assert res["error"] == {"code": "transfer_rejected", "message": "device is in service"}
    assert world.device.owner_id == world.alice.partner_id


# --- bookings -----------------------------------------------------------------------


def test_booking_is_created_for_the_callers_own_device(world):
    with _as(world, world.alice) as ctrl:
        res = ctrl.bookings(
            device_id=world.device.id,
            fault_description="  Battery drains fast ",
            service_type="collection",
            slot="evening",
            slot_date="2026-11-01",
            order_category="amc",
        )
        listed = ctrl.bookings()
    order = world.env["fix.service.order"].browse(res["booking"]["id"])
    assert res["booking"]["branch"] == "CP Dhanmondi"
    assert res["booking"]["service_type"] == "collection"
    assert order.customer_id == world.alice.partner_id
    assert order.order_category == "amc"
    assert order.priority == "normal"
    assert order.fault_description == (
        "[COLLECTION | Slot: evening | Date: 2026-11-01] Battery drains fast"
    )
    assert [b["id"] for b in listed["bookings"]] == [order.id]
    assert listed["bookings"][0]["device"] == "CP Phone X"
    assert listed["bookings"][0]["category"] == "amc"


def test_booking_cannot_self_classify_or_self_prioritise(world):
    """Regression: order_category/priority were taken verbatim from the caller -
    a customer could book zero-charge 'goodwill' work at 'emergency' priority."""
    with _as(world, world.alice) as ctrl:
        goodwill = ctrl.bookings(
            device_id=world.device.id, fault_description="x", order_category="goodwill"
        )
        urgent = ctrl.bookings(
            device_id=world.device.id, fault_description="x", priority="emergency"
        )
    order = world.env["fix.service.order"].browse(urgent["booking"]["id"])
    assert goodwill["error"]["code"] == "invalid_category"
    assert order.priority == "normal"
    assert order.order_category == "standard"


def test_booking_requires_an_owned_existing_device(world):
    with _as(world, world.bob) as ctrl:
        missing = ctrl.bookings(fault_description="x")
        foreign = ctrl.bookings(device_id=world.device.id, fault_description="x")
        unknown = ctrl.bookings(device_id=999999999, fault_description="x")
    assert missing["error"]["code"] == "missing_device"
    assert foreign["error"]["code"] == "not_owner"
    assert unknown["error"]["code"] == "not_owner"


def test_booking_branch_resolution(world):
    other = world.env["fix.branch"].create(
        {
            "name": "CP Uttara",
            "code": "CPUT",
            "entity_id": world.branch.entity_id.id,
            "operating_unit_id": world.branch.operating_unit_id.id,
        }
    )
    roaming = world.env["fix.device"].create(
        {
            "device_model_id": world.model.id,
            "owner_id": world.alice.partner_id.id,
            "serial_number": "SN-CP-ROAM",
        }
    )
    with _as(world, world.alice) as ctrl:
        chosen = ctrl.bookings(device_id=world.device.id, fault_description="x", branch_id=other.id)
        bogus = ctrl.bookings(device_id=world.device.id, fault_description="x", branch_id=999999)
        fallback = ctrl.bookings(device_id=roaming.id, fault_description="x", service_type="moon")
    assert chosen["booking"]["branch"] == "CP Uttara"
    assert bogus["error"]["code"] == "no_branch"
    assert fallback["booking"]["service_type"] == "walk_in"
    assert fallback["booking"]["branch"] in ("CP Dhanmondi", "CP Uttara")


def test_booking_without_any_branch_is_refused(world):
    device = world.env["fix.device"].create(
        {
            "device_model_id": world.model.id,
            "owner_id": world.alice.partner_id.id,
            "serial_number": "SN-CP-NOBR",
        }
    )
    with (
        patch.object(type(world.env["fix.branch"]), "search", return_value=world.env["fix.branch"]),
        _as(world, world.alice) as ctrl,
    ):
        res = ctrl.bookings(device_id=device.id, fault_description="x")
    assert res["error"]["code"] == "no_branch"


def test_warranty_booking_rides_the_models_gate(world):
    """Regression: the gate raises after the INSERT, and the rejected order used
    to stay in the (committed) request transaction."""
    with _as(world, world.alice) as ctrl:
        res = ctrl.bookings(
            device_id=world.device.id, fault_description="x", order_category="warranty"
        )
    assert res["error"]["code"] == "booking_rejected"
    assert "BRU-SRM-02" in res["error"]["message"]
    assert not world.env["fix.service.order"].search([("device_id", "=", world.device.id)])


# --- tracking detail ----------------------------------------------------------------


@pytest.mark.parametrize(
    ("state", "stage"),
    [("draft", 0), ("diagnostic", 1), ("in_repair", 2), ("qc_pending", 3), ("ready", 4)],
)
def test_tracking_reports_the_milestone_stage(world, state, stage):
    order = _order(world, state=state)
    with _as(world, world.alice) as ctrl:
        res = ctrl.tracking(order_id=order.id)["tracking"]
    assert res["current_stage"] == stage
    assert [s["completed"] for s in res["stages"]] == [i <= stage for i in range(5)]
    assert res["device"] == "CPBrand CP Phone X"
    assert res["branch"] == "CP Dhanmondi"
    assert res["legacy_reference"] is None


def test_tracking_lists_the_callers_orders(world):
    order = _order(world)
    with _as(world, world.alice) as ctrl:
        res = ctrl.tracking()
    assert [o["id"] for o in res["orders"]] == [order.id]
    assert res["orders"][0]["device"] == "CPBrand CP Phone X"


# --- estimates ----------------------------------------------------------------------


def test_estimates_list_only_the_customers_sent_estimates(world):
    order = _order(world)
    sent = _estimate(world, order, 1000.0)
    world.env["fix.estimate.line"].create(
        {
            "estimate_id": sent.id,
            "line_type": "diagnostic",
            "description": "Diagnostic fee",
            "unit_price": 300.0,
        }
    )
    _estimate(world, order, 500.0, state="draft")
    with _as(world, world.alice) as ctrl:
        mine = ctrl.estimates()
    with _as(world, world.bob) as ctrl:
        theirs = ctrl.estimates()
    [row] = mine["estimates"]
    assert row["id"] == sent.id
    # parts 1,000 + diagnostic 300 = 1,300; VAT 15% = 195; total 1,495
    assert (row["parts_total_bdt"], row["diagnostic_total_bdt"]) == ("1,000.00", "300.00")
    assert row["vat_amount_bdt"] == "195.00"
    assert row["grand_total_bdt"] == "1,495.00"
    assert row["device"] == "CPBrand CP Phone X"
    assert theirs == {"estimates": [], "total": 0}


def test_estimate_actions_are_validated(world):
    order = _order(world)
    sent = _estimate(world, order, 1000.0)
    draft = _estimate(world, order, 1000.0, state="draft")
    with _as(world, world.bob) as ctrl:
        foreign = ctrl.estimates(estimate_id=sent.id, action="approve", approval_ref="OTP-1")
    with _as(world, world.alice) as ctrl:
        bad_action = ctrl.estimates(estimate_id=sent.id, action="haggle")
        unknown = ctrl.estimates(estimate_id="nope", action="approve")
        early = ctrl.estimates(estimate_id=draft.id, action="approve", approval_ref="OTP-1")
        no_ref = ctrl.estimates(estimate_id=sent.id, action="approve")
    assert foreign["error"]["code"] == "not_your_estimate"
    assert bad_action["error"]["code"] == "invalid_action"
    assert unknown["error"]["code"] == "no_estimate"
    assert early["error"]["code"] == "estimate_not_pending"
    assert no_ref["error"]["code"] == "missing_approval_ref"
    assert (sent.state, draft.state) == ("sent", "draft")


def test_customer_approves_or_rejects_a_sent_estimate(world):
    order = _order(world)
    small = _estimate(world, order, 1000.0)
    other = _estimate(world, order, 1000.0)
    with _as(world, world.alice) as ctrl:
        approved = ctrl.estimates(estimate_id=small.id, action="approve", approval_ref="OTP-77")
        rejected = ctrl.estimates(estimate_id=other.id, action="reject")
        again = ctrl.estimates(estimate_id=other.id, action="approve", approval_ref="OTP-78")
    assert approved["estimate"] == {
        "id": small.id,
        "state": "approved",
        "customer_approval_ref": "OTP-77",
    }
    assert rejected["estimate"]["state"] == "rejected"
    assert again["error"]["code"] == "estimate_not_pending"


def test_large_estimates_wait_for_the_branch_manager(world):
    order = _order(world)
    big = _estimate(world, order, 30000.0)  # 34,500 incl. VAT > BDT 25,000
    with _as(world, world.alice) as ctrl:
        first = ctrl.estimates(estimate_id=big.id, action="approve", approval_ref="ESIGN-9")
    assert first["estimate"]["pending_manager"] is True
    assert big.state == "sent"
    assert big.customer_approval_ref == "ESIGN-9"
    big.manager_approval_uid = world.staff
    with _as(world, world.alice) as ctrl:
        second = ctrl.estimates(estimate_id=big.id, action="approve", approval_ref="ESIGN-9")
    assert second["estimate"]["state"] == "approved"


def test_model_gate_failures_are_reported(world):
    order = _order(world)
    empty = _estimate(world, order, 0)  # no lines: the model refuses approval
    with _as(world, world.alice) as ctrl:
        res = ctrl.estimates(estimate_id=empty.id, action="approve", approval_ref="OTP-1")
    assert res["error"]["code"] == "estimate_rejected"
    assert empty.state == "sent"
    assert not empty.customer_approval_ref  # a refused approval records nothing


# --- PDPA consent -------------------------------------------------------------------


def _publish_notice(world, version="1.0"):
    """Consent capture requires a published transparency notice (BRU-CPM-08);
    the grant path cannot be exercised without one."""
    return (
        world.env["fix.transparency.notice"]
        .sudo()
        .create(
            {
                "version": version,
                "purpose_set": "service,marketing",
                "text_en": "Test notice: how 1000 FiX uses your data.",
                "text_bn": "পরীক্ষামূলক বিজ্ঞপ্তি: ১০০০ ফিক্স আপনার তথ্য যেভাবে ব্যবহার করে।",
            }
        )
    )


def test_consent_grant_refused_when_no_notice_is_published(world):
    """With no published notice there is nothing lawful to capture consent
    against, and the caller is told so instead of hitting the model constraint."""
    assert not world.env["fix.transparency.notice"].sudo().search([("active", "=", True)])
    with _as(world, world.alice) as ctrl:
        refused = ctrl.consent(action="grant", channel="sms", proof="OTP-REF-0")
    assert refused["error"]["code"] == "no_transparency_notice"


def test_consent_grant_list_and_withdraw(world):
    notice = _publish_notice(world)
    with _as(world, world.alice) as ctrl:
        bad_action = ctrl.consent(action="sell")
        bad_channel = ctrl.consent(action="grant", channel="fax")
        nothing = ctrl.consent(action="withdraw", channel="sms")
        no_proof = ctrl.consent(action="grant", channel="sms")
        granted = ctrl.consent(action="grant", channel="sms", proof="OTP-REF-1")
        dashboard = ctrl.consent()
        withdrawn = ctrl.consent(action="withdraw", channel="sms")
        after = ctrl.consent()
    with _as(world, world.bob) as ctrl:
        bobs = ctrl.consent()
    assert bad_action["error"]["code"] == "invalid_action"
    assert bad_channel["error"]["code"] == "invalid_channel"
    assert nothing["error"]["code"] == "nothing_to_withdraw"
    assert no_proof["error"]["code"] == "missing_proof"
    assert granted["consent"]["state"] == "granted"
    # the grant records the notice version it was captured against (BRU-CPM-08)
    assert granted["consent"]["notice_version"] == notice.version
    assert (
        world.env["fix.consent"].sudo().browse(granted["consent"]["id"]).notice_version_id == notice
    )
    [row] = dashboard["consents"]
    assert (row["channel"], row["state"], row["proof"]) == ("sms", "granted", "OTP-REF-1")
    assert row["date_withdrawn"] is None
    assert withdrawn["consent"] == {"channel": "sms", "state": "withdrawn"}
    # PDPA T-09 is append-only: the grant is never rewritten. It is marked
    # `superseded` and a `withdrawn` record is APPENDED pointing back at it, so the
    # dashboard carries both rows. (These assertions previously expected the grant
    # itself to flip to `withdrawn`; they had never run, because the grant above
    # died on the BRU-CPM-08 constraint — re-audit 2026-10-31.) Both rows share a
    # channel and a date_granted, so assert on content, never on row order.
    assert {r["state"] for r in after["consents"]} == {"superseded", "withdrawn"}
    [wd] = [r for r in after["consents"] if r["state"] == "withdrawn"]
    [sup] = [r for r in after["consents"] if r["state"] == "superseded"]
    assert wd["date_withdrawn"] and wd["proof"] == "OTP-REF-1"
    assert sup["date_withdrawn"] is None
    assert bobs == {"consents": [], "total": 0}
