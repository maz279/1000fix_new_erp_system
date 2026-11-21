"""A04 ERP audit (20 Nov 2026) M38-F5: the Storefront Manager implies the new
Storefront Assisted Sales role. The groups file is noupdate, so the
implication defined there does not reach an existing database on upgrade:
add it here, which also gives every current manager the role (Odoo
propagates an implied group to the group's members)."""

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    manager = env.ref("cd_storefront.group_fix_storefront_manager", raise_if_not_found=False)
    assisted = env.ref(
        "cd_storefront.group_fix_storefront_assisted_sales", raise_if_not_found=False
    )
    if manager and assisted and assisted not in manager.implied_ids:
        manager.write({"implied_ids": [(4, assisted.id)]})
