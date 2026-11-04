# cd_wms_structure tests — M41 W3 slice (P06-M07) and the A06 inventory roles.
#
# A06 audit M15-17/M41-8: the checks here used to grep the source
# (inspect.getsource(...) contains "quarantine"). They are replaced by
# executed behaviour: the zone rule, the bin rules and the roles this addon
# ships (S1).
import itertools
import uuid

import pytest
from odoo.exceptions import ValidationError

SK = "cd_wms_structure.group_storekeeper"
OP = "cd_wms_structure.group_warehouse_operator"
IC = "cd_wms_structure.group_inventory_controller"
_SEQ = itertools.count(1)


def _user(env, *groups):
    n = next(_SEQ)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "WMS Structure User %d" % n,
                "login": "wms.structure.%s.%d@a06.test" % (uuid.uuid4().hex[:6], n),
                "group_ids": [(6, 0, ids)],
            }
        )
    )


@pytest.fixture
def zone(odoo_env):
    ou = odoo_env["operating.unit"].search([("company_id", "=", odoo_env.company.id)], limit=1)
    warehouse = odoo_env["fix.warehouse"].create(
        {"name": "Structure WH", "code": "W" + uuid.uuid4().hex[:6], "operating_unit_id": ou.id}
    )
    return odoo_env["fix.warehouse.zone"].create(
        {"warehouse_id": warehouse.id, "name": "Q", "code": "Q", "zone_type": "quarantine"}
    )


def test_quarantine_and_inspection_zones_are_not_reservable(odoo_env, zone):
    """BRU-INV-08 / BRU-INV-09, executed (it used to be a source grep)."""
    assert zone.reservable is False
    zone.zone_type = "inspection"
    assert zone.reservable is False
    zone.zone_type = "storage"
    assert zone.reservable is True


def test_bin_capacity_never_negative_and_storage_class(odoo_env, zone):
    Bin = odoo_env["fix.warehouse.bin"]
    assert Bin.create({"zone_id": zone.id, "name": "S-01"}).storage_class == "general"
    with pytest.raises(ValidationError, match="cannot be negative"), odoo_env.cr.savepoint():
        Bin.create({"zone_id": zone.id, "name": "S-02", "capacity_qty": -1})


def test_inventory_roles_exist_and_imply_correctly(odoo_env):
    storekeeper, operator, controller = (odoo_env.ref(x) for x in (SK, OP, IC))
    assert storekeeper in controller.all_implied_ids and operator in controller.all_implied_ids
    assert odoo_env.ref("base.group_user") in storekeeper.all_implied_ids
    admin = odoo_env.ref("base.user_admin")
    assert admin in storekeeper.user_ids and admin in operator.user_ids
    # the approver group ships EMPTY: who approves is a business appointment
    assert admin not in controller.user_ids


def test_structure_is_maintained_by_warehouse_operators_only(odoo_env, zone):
    clerk = _user(odoo_env)
    operator = _user(odoo_env, OP)
    for model in ("fix.warehouse", "fix.warehouse.zone", "fix.warehouse.bin"):
        assert odoo_env[model].with_user(clerk).has_access("read"), model
        assert not odoo_env[model].with_user(clerk).has_access("write"), model
        assert not odoo_env[model].with_user(clerk).has_access("create"), model
        assert odoo_env[model].with_user(operator).has_access("create"), model
    odoo_env["fix.warehouse.bin"].with_user(operator).create({"zone_id": zone.id, "name": "OP-01"})
