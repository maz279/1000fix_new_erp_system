"""cd_device_registry ops behaviour (live ORM, rolled back): estates, PM plans,
condition grades, identity resolution, custody events and installed components."""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from odoo.exceptions import UserError
from psycopg2 import IntegrityError

TAG = uuid.uuid4().hex[:6].upper()


def _device(env, name):
    brand = env["fix.brand"].create({"name": f"Brand {name}", "code": name[:6]})
    model = env["fix.device.model"].create({"name": f"Model {name}", "brand_id": brand.id})
    return env["fix.device"].create(
        {
            "serial_number": f"SN-{name}",
            "device_model_id": model.id,
            "owner_id": env["res.partner"].create({"name": f"Owner {name}"}).id,
        }
    )


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    return {
        "env": env,
        "device": _device(env, TAG),
        "client": env["res.partner"].create({"name": f"Estate Client {TAG}", "is_company": True}),
    }


def test_estate_assignment(ctx):
    env, device, client = ctx["env"], ctx["device"], ctx["client"]
    estate = env["fix.device.estate"].create(
        {"name": f"Estate {TAG}", "client_id": client.id, "site": "HQ"}
    )
    device.estate_id = estate.id
    assert device.estate_id == estate


def test_condition_confirm_and_battery_range(ctx):
    env, device = ctx["env"], ctx["device"]
    cond = env["fix.device.condition"].create(
        {"device_id": device.id, "grade": "b", "battery_health_pct": 90}
    )
    assert cond.name.startswith("DCON/")
    cond.action_confirm()
    assert cond.state == "confirmed"
    with pytest.raises(IntegrityError), env.cr.savepoint():  # SQL CHECK 0..100
        cond.battery_health_pct = 101


def test_pm_completion_stamps_last_done(ctx):
    env, device = ctx["env"], ctx["device"]
    pm = env["fix.device.pm"].create({"device_id": device.id, "next_due": date(2026, 11, 1)})
    assert pm.name.startswith("DPM/")
    pm.action_complete()
    assert pm.last_done


def test_identity_merge_deactivates_duplicate(ctx):
    env = ctx["env"]
    primary = ctx["device"]
    duplicate = _device(env, TAG + "D")
    identity = env["fix.device.identity"].create(
        {
            "primary_device_id": primary.id,
            "duplicate_device_id": duplicate.id,
            "match_reason": "same IMEI",
            "match_score": 99,
        }
    )
    assert identity.name.startswith("DIDR/")
    identity.action_merge()
    assert identity.state == "merged"
    assert duplicate.active is False
    with pytest.raises(UserError, match="candidate"), env.cr.savepoint():
        identity.action_merge()


def test_identity_rejects_self_merge(ctx):
    env, device = ctx["env"], ctx["device"]
    identity = env["fix.device.identity"].create(
        {
            "primary_device_id": device.id,
            "duplicate_device_id": device.id,
            "match_reason": "self",
        }
    )
    with pytest.raises(UserError, match="itself"), env.cr.savepoint():
        identity.action_merge()


def test_custody_event_sequence(ctx):
    env, device = ctx["env"], ctx["device"]
    event = env["fix.device.custody"].create(
        {"device_id": device.id, "event": "issued", "reference": f"SO-{TAG}"}
    )
    assert event.name.startswith("DCUS/")


def test_component_remove(ctx):
    env, device = ctx["env"], ctx["device"]
    component = env["fix.device.component"].create(
        {"device_id": device.id, "part_name": "Battery pack", "installed_on": date(2026, 10, 1)}
    )
    component.action_remove()
    assert component.state == "removed"
    assert component.removed_on
    with pytest.raises(UserError, match="installed"), env.cr.savepoint():
        component.action_remove()
