# res.users guards owned by M29 (A12 R2, A12 finish E24, E25). The SoD gates on
# group writes live in res_users_sod.py and fix_sod_grant_hooks.py.
from odoo import api, models
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"
    _description = "Res Users M29 SoD Gate"

    def _fix_is_portal_with_workspace(self) -> bool:
        """An external (share) identity holding an internal P03 workspace group."""
        self.ensure_one()
        base = self.env.ref("cd_rbac_ext.group_fix_portal_user", raise_if_not_found=False)
        user = self.sudo()
        return bool(base and user.share and base in user.all_group_ids)

    @api.constrains("group_ids")
    def _check_no_workspace_on_portal_user(self):
        for user in self:
            if user._fix_is_portal_with_workspace():
                raise ValidationError(
                    "%s is an external (portal) identity: internal workspace groups cannot be "
                    "given to it." % user.sudo().login
                )

    def write(self, vals):
        reactivated = deactivated = self.browse()
        if "active" in vals and not self.env.su:
            if vals["active"]:
                reactivated = self.filtered(lambda u: not u.sudo().active)
                if (
                    self.env["fix.jml.event"]
                    .sudo()
                    .search_count(
                        [
                            ("user_id", "in", reactivated.ids),
                            ("event_type", "=", "leaver"),
                            ("state", "=", "applied"),
                        ]
                    )
                ):
                    raise UserError(
                        "This login was deprovisioned by a leaver event. It returns only "
                        "through an approved joiner event, so the access is approved, "
                        "SoD-checked and audited."
                    )
            else:
                deactivated = self.filtered(lambda u: u.sudo().active)
        res = super().write(vals)
        for users, what in ((reactivated, "reactivated"), (deactivated, "deactivated")):
            for user in users:
                self.env["fix.security.audit"].log_event(
                    "user_active",
                    "res.users,%d" % user.id,
                    "login %s %s by %s" % (user.sudo().login, what, self.env.user.name),
                )
        return res
