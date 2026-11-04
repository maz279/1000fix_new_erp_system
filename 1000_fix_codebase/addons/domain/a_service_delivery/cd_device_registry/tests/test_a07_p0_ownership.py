"""A07 P0 (E1): device ownership and identifiers change only through their
controlled paths, attacked as NON-ADMIN users on the live ORM (``odoo_env``:
fix_test, rolled back). Each refusal is paired with the proper path still working.

A07 audit 2026-11-03, M17-1/M17-2/M17-5: any internal user could reassign a
customer's device (owner write, the customer endpoint's ``partner_id``), rewrite
or move an IMEI, forge ownership history, and the warranty label never expired.
"""

import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError

TAG = "A7P0"
AGENT = "cd_device_registry.group_device_registry_user"
QM = "cd_device_registry.group_device_quality_manager"


def _doc(c):
    att = c.env["ir.attachment"].create({"name": "deed.pdf", "raw": b"%PDF-1.4 a7p0"})
    return (
        c.env["fix.document"]
        .create({"name": "Sale deed", "attachment_id": att.id, "document_type": "contract"})
        .id
    )


def _user(env, login, groups=()):
    ou = env["operating.unit"].search([], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    brand = env["fix.brand"].create({"name": f"{TAG} Brand", "code": TAG})
    model = env["fix.device.model"].create({"name": f"{TAG} Phone", "brand_id": brand.id})
    x = types.SimpleNamespace(env=env, model=model)
    # A07 P1 (2026-11-04): a transfer is recorded by a Device Registry Agent
    # with a reason and evidence; an identifier is corrected by the Device
    # Quality Manager (it was base.group_system until the role existed).
    x.clerk = _user(env, f"{TAG.lower()}_clerk", [AGENT])
    x.admin = _user(env, f"{TAG.lower()}_admin", [QM])
    x.owner = env["res.partner"].create({"name": f"{TAG} Owner"})
    x.buyer = env["res.partner"].create({"name": f"{TAG} Buyer"})
    x.device = env["fix.device"].create(
        {
            "device_model_id": model.id,
            "serial_number": f"{TAG}-SN-1",
            "imei_1": "356938035643809",
            "owner_id": x.owner.id,
        }
    )
    x.as_clerk = x.device.with_user(x.clerk)
    return x


def test_owner_cannot_be_overwritten_but_first_capture_is_open(c):
    with pytest.raises(UserError, match="ownership transfer"), c.env.cr.savepoint():
        c.as_clerk.write({"owner_id": c.buyer.id})
    unowned = c.env["fix.device"].create(
        {"device_model_id": c.model.id, "serial_number": f"{TAG}-SN-2"}
    )
    unowned.with_user(c.clerk).write({"owner_id": c.owner.id})
    assert unowned.owner_id == c.owner


def test_identifiers_cannot_be_overwritten_or_moved(c):
    with pytest.raises(UserError, match="cannot be overwritten"), c.env.cr.savepoint():
        c.as_clerk.write({"imei_1": "490154203237518"})
    with pytest.raises(UserError, match="cannot be overwritten"), c.env.cr.savepoint():
        c.as_clerk.write({"serial_number": False})
    # an empty identifier can still be captured, and echoing the same value is fine
    c.as_clerk.write({"imei_2": "490154203237518", "imei_1": "356938035643809"})
    assert c.device.imei_2 == "490154203237518"


def test_transfer_records_history_and_refuses_lost_devices(c):
    c.as_clerk.action_transfer_ownership(
        c.buyer.id, transfer_type="gift", notes="family", evidence_document_id=_doc(c)
    )
    assert c.device.owner_id == c.buyer and c.device.state == "transferred"
    row = c.env["fix.device.ownership"].search([("device_id", "=", c.device.id)])
    assert (row.from_partner_id, row.to_partner_id, row.transfer_type) == (c.owner, c.buyer, "gift")
    assert row.transfer_date == fields.Date.context_today(c.device)

    lost = c.env["fix.device"].create(
        {
            "device_model_id": c.model.id,
            "serial_number": f"{TAG}-SN-3",
            "owner_id": c.owner.id,
            "state": "lost",
        }
    )
    with pytest.raises(UserError, match="cannot change owner"), c.env.cr.savepoint():
        lost.with_user(c.clerk).action_transfer_ownership(c.buyer.id)


def test_ownership_history_is_insert_only_for_users(c):
    c.as_clerk.action_transfer_ownership(c.buyer.id, reason="sale", evidence_document_id=_doc(c))
    row = c.env["fix.device.ownership"].search([("device_id", "=", c.device.id)]).with_user(c.clerk)
    for attack in (
        lambda: row.write({"to_partner_id": c.owner.id}),
        lambda: row.unlink(),
        lambda: row.create({"device_id": c.device.id, "to_partner_id": c.owner.id}),
    ):
        with pytest.raises(UserError, match="permanent record"), c.env.cr.savepoint():
            attack()


def test_identifier_correction_is_privileged_and_logged(c):
    with pytest.raises(AccessError), c.env.cr.savepoint():
        c.as_clerk.action_correct_identifier("imei_1", "490154203237518", "board swap")
    as_admin = c.device.with_user(c.admin)
    with pytest.raises(UserError, match="reason"), c.env.cr.savepoint():
        as_admin.action_correct_identifier("imei_1", "490154203237518", "  ")
    as_admin.action_correct_identifier("imei_1", "490154203237518", "board swap J-17")
    assert c.device.imei_1 == "490154203237518"
    assert any("board swap J-17" in (m.body or "") for m in c.device.message_ids)


def test_customer_endpoint_transfers_only_as_the_owner(c):
    import odoo.addons.cd_customer_portal.controllers.customer_api as capi

    ctl = capi.CustomerApiController()
    endpoint = capi.CustomerApiController.ownership_transfer
    endpoint = getattr(endpoint, "original_endpoint", endpoint)
    old = getattr(capi, "request", None)
    try:
        # staff login acting for the owner via partner_id: refused
        capi.request = types.SimpleNamespace(env=c.env(user=c.clerk.id))
        out = endpoint(ctl, device_id=c.device.id, to_partner_id=c.buyer.id, partner_id=c.owner.id)
        assert not out.get("transferred") and c.device.owner_id == c.owner
        # the owner's own portal login: allowed
        portal = (
            c.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": f"{TAG} Portal",
                    "login": f"{TAG.lower()}_portal",
                    "partner_id": c.owner.id,
                    "group_ids": [(6, 0, [c.env.ref("base.group_portal").id])],
                }
            )
        )
        capi.request = types.SimpleNamespace(env=c.env(user=portal.id))
        out = endpoint(ctl, device_id=c.device.id, to_partner_id=c.buyer.id)
        assert out.get("transferred") and c.device.owner_id == c.buyer
    finally:
        capi.request = old


def test_warranty_label_follows_the_date_and_is_searchable(c):
    today = fields.Date.context_today(c.device)
    w = c.env["fix.warranty"].create(
        {
            "device_id": c.device.id,
            "start_date": today - timedelta(days=400),
            "end_date": today - timedelta(days=1),
            "status": "active",  # superuser fixture; users are born pending
        }
    )
    c.device.invalidate_recordset(["warranty_status"])
    assert c.device.warranty_status == "out_of_warranty"
    Device = c.env["fix.device"]
    assert c.device not in Device.search([("warranty_status", "=", "in_warranty")])
    assert c.device in Device.search([("warranty_status", "=", "out_of_warranty")])
    assert c.device in Device.search([("warranty_status", "!=", "unknown")])
    w.sudo()._guarded().write({"end_date": today + timedelta(days=30)})
    c.device.invalidate_recordset(["warranty_status"])
    assert c.device.warranty_status == "in_warranty"
    assert c.device in Device.search([("warranty_status", "in", ["in_warranty", "extended"])])
