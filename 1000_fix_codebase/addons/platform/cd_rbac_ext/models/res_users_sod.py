# res.users — the preventive SoD gate on the real permission surface
# (A10 P1-3, M60-5).
#
# The audit found the 61-control register enforced nowhere that mattered:
# no fix.role had a group mapped, and the raw group write — the operation
# that actually hands a person power — checked nothing. Adding a group is
# now checked against the person's full register set: every fix.role whose
# group is in the final set, plus the roles their employee master carries.
# Removals are never blocked (shrinking a set creates no conflict) and
# groups outside the register pass untouched.
from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        self.env["fix.sod.control"]._check_new_user_groups(vals_list)
        return super().create(vals_list)

    def write(self, vals):
        commands = vals.get("group_ids", vals.get("groups_id"))
        if commands is not None:
            self.env["fix.sod.control"]._check_users_group_write(self, commands)
        return super().write(vals)
