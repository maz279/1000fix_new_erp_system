"""M03 extension tests: POD with OTP, the reachable in_transit state, the
guarded confirm, and the service-order bridge.

``odoo_env`` (addons/conftest.py): fix_test, rolled back after every test.
"""

from datetime import datetime

import pytest
from odoo.exceptions import UserError


@pytest.fixture
def lg(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    # one legal entity per company (fix_entity_company_unique): reuse it
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": "LGEXT", "legal_name": "Logistics Ext Entity", "company_id": env.company.id})
    branch = env["fix.branch"].create(
        {
            "name": "LG Ext Branch",
            "code": "LGE1",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    other = env["fix.branch"].create(
        {
            "name": "LG Ext Branch 2",
            "code": "LGE2",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "LgExtBrand", "code": "LGE"})
    device_model = env["fix.device.model"].create({"name": "LgExt Phone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "LG Customer", "phone": "01711000303"})
    device = env["fix.device"].create(
        {"device_model_id": device_model.id, "owner_id": customer.id, "serial_number": "SN-LGE-1"}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "Collection pickup test",
            "service_type": "collection",
        }
    )
    rider = env["hr.employee"].create({"name": "LG Rider"})

    def consignment(**vals):
        base = {
            "consignment_type": "pickup",
            "scheduled_date": datetime.now(),
            "origin_branch_id": other.id,
            "dest_branch_id": branch.id,
            "service_order_id": order.id,
            "operating_unit_id": ou.id,
            "rider_id": rider.id,
            "declared_value_bdt": 1000.0,  # BRU-LOG-12: needed to confirm
        }
        base.update(vals)
        return env["fix.consignment"].create(base)

    from types import SimpleNamespace

    return SimpleNamespace(
        env=env, branch=branch, other=other, order=order, rider=rider, consignment=consignment
    )


@pytest.fixture
def sms(odoo_env, monkeypatch):
    """Capture the POD code instead of handing it to the SMS dispatcher."""
    sent = []
    monkeypatch.setattr(
        odoo_env.registry["fix.consignment"],
        "_pod_send_otp",
        lambda self, phone, code: sent.append((phone, code)),
    )
    return sent


# --- state machine guards -------------------------------------------------


def test_confirm_refuses_non_draft(lg):
    cons = lg.consignment()
    cons.action_confirm()
    cons.state = "in_transit"
    with pytest.raises(UserError, match="Only draft consignments"):
        cons.action_confirm()


def test_start_transit_reachable_and_stamps_first_scan(lg):
    cons = lg.consignment()
    cons.action_confirm()
    cons.action_start_transit()
    assert cons.state == "in_transit"
    assert cons.custody_ids[:1].step == "picked_up"  # chain auto-started
    assert cons.custody_ids.mapped("step") == ["picked_up", "in_transit"]
    assert not cons.chain_broken


def test_start_transit_requires_confirmed(lg):
    cons = lg.consignment()
    with pytest.raises(UserError, match="Only confirmed consignments"):
        cons.action_start_transit()


# --- POD with OTP -----------------------------------------------------------


def test_pod_otp_full_flow(lg, sms):
    cons = lg.consignment(consignment_type="delivery")
    cons.action_confirm()
    cons.action_start_transit()
    cons.action_out_for_delivery()
    cons.action_generate_otp()
    # A02 audit M03-4: the code goes to the customer's phone and is kept
    # only as a keyed hash.
    ((phone, otp),) = sms
    assert phone == "01711000303" and len(otp) == 6
    assert cons.sudo().pod_otp_hash and otp not in cons.sudo().pod_otp_hash
    with pytest.raises(UserError, match="POD OTP mismatch"), cons.env.cr.savepoint():
        cons.action_verify_pod("000000")
    assert cons.state == "in_transit"  # refused — device stays in custody
    cons.action_verify_pod(otp)
    assert cons.state == "delivered"
    assert cons.pod_verified_at and cons.pod_verified_by and cons.delivered_at
    assert not cons.sudo().pod_otp_hash  # single-use
    assert cons.custody_ids[-1:].step == "delivered"
    assert not cons.chain_broken


def test_pod_requires_issued_otp(lg):
    cons = lg.consignment(consignment_type="delivery")
    cons.action_confirm()
    cons.action_start_transit()
    with pytest.raises(UserError, match="No POD OTP"):
        cons.action_verify_pod("123456")


def test_generate_otp_only_in_transit(lg):
    cons = lg.consignment(consignment_type="delivery")
    with pytest.raises(UserError, match="issued for consignments in transit"):
        cons.action_generate_otp()


def test_lost_refuses_delivered(lg, sms):
    cons = lg.consignment(consignment_type="delivery")
    cons.action_confirm()
    cons.action_start_transit()
    cons.action_out_for_delivery()
    cons.action_generate_otp()
    cons.action_verify_pod(sms[-1][1])
    with pytest.raises(UserError, match="cannot be reported lost"):
        cons.action_report_lost()


# --- service-order bridge ----------------------------------------------------


def test_bridge_creates_pickup_for_collection(lg):
    created = lg.order.action_create_consignment()
    assert len(created) == 1
    assert created.consignment_type == "pickup"
    assert created.dest_branch_id == lg.branch
    assert created.service_order_id == lg.order
    assert lg.order.consignment_count == 1


def test_bridge_creates_delivery_for_onsite(lg):
    lg.order.service_type = "onsite"
    created = lg.order.action_create_consignment()
    assert created.consignment_type == "delivery"
    assert created.origin_branch_id == lg.branch


def test_bridge_refuses_closed(lg):
    lg.order.state = "intake"
    lg.order.state = "diagnostic"
    lg.order.state = "estimate_pending"
    lg.order.state = "estimate_sent"
    lg.order.state = "awaiting_approval"
    lg.order.state = "approved"
    lg.order.state = "in_repair"
    lg.order.state = "qc_pending"
    # M01 reads the checklist of the current QC round (qc_round)
    lg.env["fix.qc.checklist"].create(
        {"order_id": lg.order.id, "state": "passed", "qc_round": lg.order.qc_round}
    )
    lg.order.state = "ready"
    lg.order.state = "delivered"
    lg.order.state = "closed"
    with pytest.raises(UserError, match="no new logistics legs"):
        lg.order.action_create_consignment()


# --- M03 capture audit 2026-11-18: the hand-over raises the NEXT leg ----------


def _arrive(cons):
    """A pickup leg through to its receipt at the branch (the device is home)."""
    cons.declared_value_bdt = 1000.0  # BRU-LOG-12
    cons.action_confirm()
    cons.action_start_transit()
    cons.action_verify_hub_intake()
    cons.action_confirm_receipt()
    assert cons.state == "delivered"
    return cons


def _ready(order):
    for state in (
        "intake",
        "diagnostic",
        "estimate_pending",
        "estimate_sent",
        "awaiting_approval",
        "approved",
        "in_repair",
        "qc_pending",
    ):
        order.state = state
    order.env["fix.qc.checklist"].create(
        {"order_id": order.id, "state": "passed", "qc_round": order.qc_round}
    )
    order.state = "ready"


def test_bridge_sends_no_second_pickup_once_the_device_arrived(lg):
    """It raised another pickup: a rider sent for a device already in the shop."""
    _arrive(lg.order.action_create_consignment())
    lg.order.state = "intake"
    lg.order.state = "diagnostic"
    with pytest.raises(UserError, match="already arrived at the branch"):
        lg.order.action_create_consignment()
    assert lg.order.consignment_count == 1


def test_bridge_raises_the_delivery_back_when_the_order_is_ready(lg):
    """The return leg of a collection journey could not be raised at all."""
    _arrive(lg.order.action_create_consignment())
    _ready(lg.order)
    back = lg.order.action_create_consignment()
    assert back.consignment_type == "delivery"
    assert back.origin_branch_id == lg.branch and not back.dest_branch_id
    assert back.service_order_id == lg.order
    with pytest.raises(UserError, match="already has a live leg"):
        lg.order.action_create_consignment()


def test_bridge_collects_again_after_a_failed_pickup(lg):
    """A pickup that came back without the device does not count as arrived."""
    first = lg.order.action_create_consignment()
    first.declared_value_bdt = 1000.0
    first.action_confirm()
    first.action_return(reason="Customer not at home")
    assert first.state == "returned"
    again = lg.order.action_create_consignment()
    assert again.consignment_type == "pickup" and again != first


def test_bridge_delivers_a_ready_collection_order_that_was_dropped_off(lg):
    """The customer brought it in but wants it delivered back: no pickup."""
    _ready(lg.order)
    assert lg.order.action_create_consignment().consignment_type == "delivery"
