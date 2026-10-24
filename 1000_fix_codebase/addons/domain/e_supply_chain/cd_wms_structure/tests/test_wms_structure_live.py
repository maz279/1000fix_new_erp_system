# cd_wms_structure live-ORM tests — M41 warehouse structure (W3 slice).
import uuid

import pytest
from odoo.exceptions import ValidationError


@pytest.fixture
def warehouse(odoo_env):
    ou = odoo_env["operating.unit"].search([("company_id", "=", odoo_env.company.id)], limit=1)
    return odoo_env["fix.warehouse"].create(
        {"name": "Tejgaon Central", "code": f"W{uuid.uuid4().hex[:7]}", "operating_unit_id": ou.id}
    )


@pytest.mark.parametrize(
    ("zone_type", "reservable"),
    [
        ("receiving", True),
        ("inspection", False),  # BRU-INV-09: available only after inspection
        ("quarantine", False),  # BRU-INV-08: never reserved or issued
        ("storage", True),
        ("dispatch", True),
        ("returns", True),
    ],
)
def test_zone_reservability(odoo_env, warehouse, zone_type, reservable):
    zone = odoo_env["fix.warehouse.zone"].create(
        {
            "warehouse_id": warehouse.id,
            "name": zone_type,
            "code": zone_type[:8],
            "zone_type": zone_type,
        }
    )
    assert zone.reservable is reservable


def test_zone_reservability_follows_its_type(odoo_env, warehouse):
    zone = odoo_env["fix.warehouse.zone"].create(
        {"warehouse_id": warehouse.id, "name": "Main", "code": "MAIN"}
    )
    assert (zone.zone_type, zone.reservable) == ("storage", True)
    zone.zone_type = "quarantine"
    assert zone.reservable is False


def test_bin_capacity(odoo_env, warehouse):
    zone = odoo_env["fix.warehouse.zone"].create(
        {"warehouse_id": warehouse.id, "name": "Main", "code": "MAIN"}
    )
    Bin = odoo_env["fix.warehouse.bin"]
    unconstrained = Bin.create({"zone_id": zone.id, "name": "A-01-01"})
    sized = Bin.create({"zone_id": zone.id, "name": "A-01-02", "capacity_qty": 40.0})
    assert (unconstrained.capacity_qty, sized.capacity_qty) == (0.0, 40.0)
    assert warehouse.zone_ids == zone
    assert zone.bin_ids == unconstrained | sized


def test_negative_bin_capacity_is_refused(odoo_env, warehouse):
    zone = odoo_env["fix.warehouse.zone"].create(
        {"warehouse_id": warehouse.id, "name": "Main", "code": "MAIN"}
    )
    with (
        pytest.raises(ValidationError, match="Bin capacity cannot be negative"),
        odoo_env.cr.savepoint(),
    ):
        odoo_env["fix.warehouse.bin"].create(
            {"zone_id": zone.id, "name": "A-01-03", "capacity_qty": -1.0}
        )
