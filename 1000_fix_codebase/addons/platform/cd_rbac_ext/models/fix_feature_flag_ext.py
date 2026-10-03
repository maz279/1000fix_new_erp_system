# fix.feature.flag role scoping (P03-M02/M29) — the fix.role-aware extension.
# The PLATFORM layer's fix.feature.flag cannot reference fix.role (cd_rbac_ext
# depends on cd_entity_config, never the reverse); scope="role" fails CLOSED
# in the base model. Here — where fix.role exists — the role_ids field and
# the role-scoped check live.
from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class FixFeatureFlagRoleExt(models.Model):
    _inherit = "fix.feature.flag"

    role_ids = fields.Many2many("fix.role", string="Enabled Roles",
                                help="Only used when scope=role (M29 fix.role)")

    @api.model
    def is_enabled(self, key: str, branch=None, role=None) -> bool:
        """Role-scoped extension of the base fail-closed check."""
        flag = self.sudo().search([("key", "=", key), ("active", "=", True)], limit=1)
        if not flag or not flag.enabled:
            return False
        if flag.scope == "role" and role:
            return role in flag.role_ids
        return super().is_enabled(key, branch=branch, role=role)
