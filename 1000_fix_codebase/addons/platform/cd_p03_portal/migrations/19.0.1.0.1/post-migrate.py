# Restore Odoo's Discuss app, which earlier versions of this module overrode
# (mail.action_discuss opened the P03 workspace and mail.menu_root_discuss was
# renamed "1000 FiX Operations"), leaving internal chat unreachable. Values
# are the ones vendor/odoo/addons/mail ships.
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    action = env.ref("mail.action_discuss", raise_if_not_found=False)
    if action:
        action.write(
            {
                "name": "Discuss",
                "tag": "mail.action_discuss",
                "path": "discuss",
                "params": {"default_active_id": "mail.box_inbox"},
            }
        )
    menu = env.ref("mail.menu_root_discuss", raise_if_not_found=False)
    if menu and action:
        menu.write({"name": "Discuss", "action": f"ir.actions.client,{action.id}", "sequence": 5})
