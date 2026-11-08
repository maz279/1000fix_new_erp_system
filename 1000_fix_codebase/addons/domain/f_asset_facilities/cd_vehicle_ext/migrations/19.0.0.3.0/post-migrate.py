# A07 operability M46-19: two groups were named "Logistics Manager" (this one and
# cd_consignment's), and granting the wrong one refused with the same name. The
# group is noupdate data, so the rename reaches an existing database here.
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    group = env.ref("cd_vehicle_ext.group_logistics_manager", raise_if_not_found=False)
    if group:
        group.update_field_translations(
            "name",
            {"en_US": "Fleet Logistics Manager", "bn_BD": "ফ্লিট লজিস্টিকস ম্যানেজার"},
        )
