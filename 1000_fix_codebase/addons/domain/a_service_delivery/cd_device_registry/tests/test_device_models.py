"""Behavioural tests for the M17 device registry on the live ORM
(``odoo_env``: fix_test, rolled back after every test)."""

import json
from contextlib import contextmanager
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from odoo import Command
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError


@contextmanager
def _refused(env, exc, match=None):
    """Expect ``exc``; the failed operation is rolled back (flushing savepoint)."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


@pytest.fixture
def reg(odoo_env):
    env = odoo_env
    brand = env["fix.brand"].create({"name": "RegBrand", "code": "REGBR"})
    model = env["fix.device.model"].create({"name": "RegBook 14", "brand_id": brand.id})
    owner = env["res.partner"].create({"name": "Reg Owner"})
    buyer = env["res.partner"].create({"name": "Reg Buyer"})
    return SimpleNamespace(env=env, brand=brand, model=model, owner=owner, buyer=buyer)


def _device(reg, **vals):
    return reg.env["fix.device"].create({"device_model_id": reg.model.id, **vals})


def _events(env, device, event_type):
    return env["fix.event.outbox"].search(
        [
            ("aggregate", "=", "fix.device"),
            ("aggregate_id", "=", device.id),
            ("event_type", "=", event_type),
        ]
    )


def test_name_and_classification_follow_the_model(reg):
    with_serial = _device(reg, serial_number="SN-REG-1")
    bare = _device(reg)
    assert with_serial.name == "RegBook 14 — S/N SN-REG-1"
    assert bare.name == "RegBook 14"
    assert with_serial.brand_id == reg.brand
    event = _events(reg.env, with_serial, "device.registered")
    assert json.loads(event.payload) == {
        "device_id": with_serial.id,
        "serial_number": "SN-REG-1",
        "brand": "RegBrand",
        "model": "RegBook 14",
        "owner_id": None,
    }


def test_warranty_status_is_derived_from_the_warranty_records(reg):
    env = reg.env
    today = date.today()
    device = _device(reg, serial_number="SN-REG-W")
    assert device.warranty_status == "unknown"  # no warranty at all
    warranty = env["fix.warranty"]
    expired = warranty.create(
        {
            "device_id": device.id,
            "start_date": today - timedelta(days=800),
            "end_date": today - timedelta(days=70),
            "status": "expired",
        }
    )
    assert device.warranty_status == "unknown"  # only non-active records
    expired.status = "active"  # active but its end date passed
    assert device.warranty_status == "out_of_warranty"
    warranty.create(
        {
            "device_id": device.id,
            "start_date": today - timedelta(days=10),
            "end_date": today + timedelta(days=355),
            "status": "active",  # A02 M01-W1: a new warranty is born pending
        }
    )
    # the most recent start date comes first (_order) and is still running
    assert device.warranty_status == "in_warranty"


def test_imei_must_be_fifteen_digits(reg):
    env = reg.env
    with _refused(env, ValidationError) as err:
        _device(reg, imei_1="12345")
    assert str(err.value) == "IMEI must be exactly 15 digits, got 5: 12345"
    with _refused(env, ValidationError, "got 15: 35693803564380A"):
        _device(reg, imei_1="35693803564380A")
    assert _device(reg, imei_1="356938035643809").imei_1 == "356938035643809"


def test_serial_and_imei_are_unique(reg):
    _device(reg, serial_number="SN-REG-DUP", imei_1="490154203237518")
    with _refused(reg.env, IntegrityError, "fix_device_serial_unique_when_set"):
        _device(reg, serial_number="SN-REG-DUP")
    with _refused(reg.env, IntegrityError, "fix_device_imei1_unique_when_set"):
        _device(reg, imei_1="490154203237518")


def test_ownership_transfer_is_recorded_and_published(reg):
    env = reg.env
    device = _device(reg, serial_number="SN-REG-T", owner_id=reg.owner.id)
    device.action_transfer_ownership(reg.buyer.id)
    assert (device.owner_id, device.state) == (reg.buyer, "transferred")
    record = env["fix.device.ownership"].search([("device_id", "=", device.id)])
    assert (record.from_partner_id, record.to_partner_id, record.transfer_date) == (
        reg.owner,
        reg.buyer,
        date.today(),
    )
    assert record.transfer_type == "sale"
    assert (
        json.loads(_events(env, device, "device.transferred").payload)["owner_id"] == reg.buyer.id
    )
    unowned = _device(reg, serial_number="SN-REG-T2")
    unowned.action_transfer_ownership(reg.owner.id)
    first = env["fix.device.ownership"].search([("device_id", "=", unowned.id)])
    assert (first.from_partner_id, first.to_partner_id) == (env["res.partner"], reg.owner)


def test_writes_publish_only_owner_and_warranty_changes(reg):
    env = reg.env
    device = _device(reg, serial_number="SN-REG-E")
    device.write({"purchase_channel": "online"})
    assert not _events(env, device, "device.transferred")
    device.write(
        {
            "warranty_id": [
                Command.create(
                    {
                        "start_date": date.today(),
                        "end_date": date.today() + timedelta(days=30),
                        "status": "active",  # A02 M01-W1: born pending otherwise
                    }
                )
            ]
        }
    )
    assert len(_events(env, device, "device.warranty_updated")) == 1
    assert device.warranty_status == "in_warranty"


def test_history_entries_are_permanent_records(reg):
    device = _device(reg, serial_number="SN-REG-H")
    device.add_history("repair", "Screen replaced")
    entry = device.history_ids
    assert (entry.event_type, entry.description, entry.service_order_id) == (
        "repair",
        "Screen replaced",
        reg.env["fix.service.order"],
    )
    assert entry.date


def test_compatible_parts_by_category(reg):
    env = reg.env
    compat = env["fix.device.part.compatibility"]
    battery = compat.create(
        {
            "model_id": reg.model.id,
            "part_number": "REG-BAT",
            "part_name": "Battery",
            "category": "battery",
        }
    )
    screen = compat.create({"model_id": reg.model.id, "part_number": "REG-LCD", "part_name": "LCD"})
    compat.create(
        {
            "model_id": reg.model.id,
            "part_number": "REG-OLD",
            "part_name": "Old LCD",
            "active": False,
        }
    )
    device = _device(reg, serial_number="SN-REG-P")
    assert device.get_compatible_parts().mapped("part_number") == ["REG-BAT", "REG-LCD"]
    assert device.get_compatible_parts() == screen | battery  # the inactive one is excluded
    assert device.get_compatible_parts("battery") == battery
    assert battery.brand_id == reg.brand
    with _refused(env, IntegrityError, "unique_model_part"):
        compat.create({"model_id": reg.model.id, "part_number": "REG-BAT", "part_name": "Dup"})


def test_under_warranty_is_decided_on_the_date(reg):
    """BRU-SRM-02 helper: an ACTIVE record covering the day, bounds included -
    independent of the stored (recompute-frozen) warranty_status."""
    env = reg.env
    device = _device(reg, serial_number="SN-REG-U")
    assert device.is_under_warranty() is False  # no record
    env["fix.warranty"].create(
        {
            "device_id": device.id,
            "start_date": date(2026, 1, 1),
            "end_date": date(2026, 6, 30),
            "status": "active",  # A02 M01-W1: a new warranty is born pending
        }
    )
    env["fix.warranty"].create(
        {
            "device_id": device.id,
            "start_date": date(2026, 7, 1),
            "end_date": date(2026, 12, 31),
            "status": "voided",
        }
    )
    assert device.is_under_warranty(date(2026, 1, 1)) is True
    assert device.is_under_warranty(date(2026, 6, 30)) is True
    assert device.is_under_warranty(date(2025, 12, 31)) is False  # before the start
    assert device.is_under_warranty(date(2026, 8, 1)) is False  # only a voided record
