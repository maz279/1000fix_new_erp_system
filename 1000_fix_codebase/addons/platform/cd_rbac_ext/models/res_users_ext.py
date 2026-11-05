# A12 R2 (M29-4): the SoD gate on the last grant path — a direct write of
# res.users.group_ids (Odoo Settings, an ORM script, any future surface).
# The access-request, JML and certification paths already gate their grants;
# this override catches everything else. Removals never conflict; additions
# are mapped back to roles and checked against every role the user holds.
from odoo import models


def _added_group_ids(current_ids, commands):
    """The group ids a group_ids command list ADDS for a user holding
    `current_ids` (removals and no-op echoes are ignored)."""
    if not isinstance(commands, list):
        return set()
    result = set(current_ids)
    for cmd in commands:
        if not cmd:
            continue
        op = cmd[0]
        if op in (3, 2):  # unlink / remove
            result.discard(cmd[1])
        elif op == 4:  # link
            result.add(cmd[1])
        elif op == 5:  # clear all
            result = set()
        elif op == 6:  # replace with ids
            result = set(cmd[2])
        elif op == 0 or op == 1:  # new record command — not a group link; ignore
            continue
    return result - set(current_ids)


class ResUsers(models.Model):
    _inherit = "res.users"
    _description = "Res Users M29 SoD Gate"

    def write(self, vals):
        if not self.env.su and "group_ids" in vals:
            Sod = self.env["fix.sod.control"]
            for user in self:
                added = _added_group_ids(user.sudo().group_ids.ids, vals["group_ids"])
                if added:
                    Sod.check_user_groups(user, added)
        return super().write(vals)
