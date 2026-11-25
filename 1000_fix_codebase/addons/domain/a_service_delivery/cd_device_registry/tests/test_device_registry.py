# Tests for cd_device_registry (P04-M01) — device, warranty, ownership, history.
#
# A07 audit (2026-11-04) P3, D10: this file asserted that methods and
# constraint attributes EXIST (`"x" in dir(FixDevice)`), which certified the
# registry whether or not any control held. Each test now exercises the
# behaviour its name claims, on the live ORM (`odoo_env`, rolled back), as a
# non-admin user where the control is about users.
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

TAG = "A7DR"


@pytest.fixture
def r(odoo_env):
    env = odoo_env
    brand = env["fix.brand"].create({"name": f"{TAG} Brand", "code": TAG})
    model = env["fix.device.model"].create({"name": f"{TAG} Model", "brand_id": brand.id})
    ou = env["operating.unit"].search([], limit=1)
    clerk = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": f"{TAG} clerk",
                "login": f"{TAG.lower()}_clerk",
                "group_ids": [(6, 0, [env.ref("base.group_user").id])],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    owner = env["res.partner"].create({"name": f"{TAG} Owner"})

    def device(**vals):
        return env["fix.device"].create({"device_model_id": model.id, "owner_id": owner.id, **vals})

    return env, clerk, owner, model, device


def _raises(env, exc, fn):
    with pytest.raises(exc), env.cr.savepoint():
        fn()
        env.flush_all()


class TestFixDevice:
    def test_model_exists(self, r):
        env, clerk, _owner, model, _device = r
        d = (
            env["fix.device"]
            .with_user(clerk)
            .create({"device_model_id": model.id, "serial_number": f"{TAG}-1"})
        )
        assert d.state == "registered" and d.name.endswith(f"S/N {TAG}-1")

    def test_serial_unique_constraint(self, r):
        env, _clerk, _owner, _model, device = r
        device(serial_number=f"{TAG}-U")
        _raises(env, IntegrityError, lambda: device(serial_number=f"{TAG}-U"))
        _raises(env, ValidationError, lambda: device(serial_number=f"{TAG.lower()}-u"))

    def test_imei1_unique_constraint(self, r):
        env, _clerk, _owner, _model, device = r
        device(imei_1="356938035643809")
        _raises(env, IntegrityError, lambda: device(imei_1="356938035643809"))

    def test_imei_format_constraint(self, r):
        env, _clerk, _owner, _model, device = r
        for vals in ({"imei_1": "12345"}, {"imei_2": "ABCDEFGHIJKLMNO"}):
            _raises(env, ValidationError, lambda v=vals: device(**v))

    def test_ownership_transfer_api(self, r):
        env, clerk, owner, _model, device = r
        d = device(serial_number=f"{TAG}-T")
        buyer = env["res.partner"].create({"name": f"{TAG} Buyer"})
        _raises(env, UserError, lambda: d.with_user(clerk).write({"owner_id": buyer.id}))
        _raises(env, AccessError, lambda: d.with_user(clerk).action_transfer_ownership(buyer.id))
        d.action_transfer_ownership(buyer.id)  # trusted service path
        row = env["fix.device.ownership"].search([("device_id", "=", d.id)])
        assert (d.owner_id, row.from_partner_id, row.to_partner_id) == (buyer, owner, buyer)

    def test_warranty_status_computed(self, r):
        env, _clerk, _owner, _model, device = r
        d = device(serial_number=f"{TAG}-W")
        today = fields.Date.context_today(d)
        assert d.warranty_status == "unknown"
        env["fix.warranty"].create(
            {
                "device_id": d.id,
                "start_date": today - timedelta(days=10),
                "end_date": today + timedelta(days=10),
                "status": "active",
            }
        )
        d.invalidate_recordset(["warranty_status"])
        assert d.warranty_status == "in_warranty"

    def test_device_history_api(self, r):
        env, clerk, _owner, _model, device = r
        d = device(serial_number=f"{TAG}-H")
        d.with_user(clerk).add_history("repair", "bench repair")
        h = env["fix.device.history"].search([("device_id", "=", d.id)])
        assert len(h) == 1 and h.event_type == "repair"
        forged = {"device_id": d.id, "event_type": "repair", "description": "x", "date": h.date}
        _raises(env, UserError, lambda: h.with_user(clerk).create(forged))
        _raises(env, AccessError, lambda: h.with_user(clerk).write({"description": "edited"}))

    def test_state_selection_present(self, r):
        env, clerk, _owner, _model, device = r
        states = dict(env["fix.device"]._fields["state"].selection)
        assert {"provisional", "registered", "lost", "scrapped"} <= set(states)
        d = device(serial_number=f"{TAG}-S")
        for state in ("scrapped", "lost", "transferred"):
            _raises(env, UserError, lambda s=state: d.with_user(clerk).write({"state": s}))
        assert d.state == "registered"


class TestFixWarranty:
    def test_model_exists(self, r):
        env, clerk, _owner, _model, device = r
        d = device(serial_number=f"{TAG}-WT")
        today = fields.Date.context_today(d)
        w = (
            env["fix.warranty"]
            .with_user(clerk)
            .create({"device_id": d.id, "start_date": today, "end_date": today + timedelta(30)})
        )
        assert w.status == "pending"
        _raises(env, UserError, lambda: w.with_user(clerk).action_verify())


class TestFixDeviceHistory:
    def test_model_exists(self, r):
        env, _clerk, _owner, _model, device = r
        d = device(serial_number=f"{TAG}-HM")
        d.add_history("other", "registered")
        # history is permanent: the device cannot be deleted from under it
        _raises(env, (IntegrityError, UserError), lambda: d.unlink())


class TestFixDeviceW2Extensions:
    def test_lifecycle_and_compatibility_fields(self, r):
        env, clerk, _owner, model, device = r
        d = device(serial_number=f"{TAG}-L")
        _raises(env, UserError, lambda: d.with_user(clerk).write({"lifecycle_stage": "vintage"}))
        d.action_set_lifecycle_stage("vintage", "parts on allocation")
        assert d.lifecycle_stage == "vintage"
        env["fix.device.part.compatibility"].create(
            {
                "model_id": model.id,
                "part_number": f"{TAG}-B",
                "part_name": "Battery",
                "category": "battery",
            }
        )
        assert d.get_compatible_parts("battery").part_number == f"{TAG}-B"

    def test_device_part_compatibility_model(self, r):
        env, clerk, _owner, model, _device = r
        Matrix = env["fix.device.part.compatibility"]
        vals = {"model_id": model.id, "part_number": f"{TAG}-X", "part_name": "Panel"}
        Matrix.create(vals)
        _raises(env, IntegrityError, lambda: Matrix.create(vals))
        # the matrix is configuration: a plain user reads it, never edits it
        other = dict(vals, part_number=f"{TAG}-Y")
        _raises(env, AccessError, lambda: Matrix.with_user(clerk).create(other))
