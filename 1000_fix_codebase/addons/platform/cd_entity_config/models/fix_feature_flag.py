# fix.feature.flag — the feature-flag service (P03-M04-T05, OPS-06/EP-07).
# Every capability from Wave 1 onward ships behind a flag.
# Usage: @flag_enabled("my_feature_key") — decorator checks this model.
from odoo import api, fields, models
from odoo.exceptions import UserError

import functools
import logging

_logger = logging.getLogger(__name__)


class FixFeatureFlag(models.Model):
    """A feature flag: any new capability is disableable without deployment."""
    _name = "fix.feature.flag"
    _description = "Feature Flag"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _sql_constraints = [
        ("key_unique", "unique(key)", "Feature flag key must be unique"),
    ]

    key = fields.Char(string="Key", required=True, index=True,
                      help="Dot-notation key, e.g. 'dispatch.auto_assign'")
    name = fields.Char(string="Description", required=True)
    enabled = fields.Boolean(default=False, tracking=True,
                             help="False = capability disabled (safe default)")
    scope = fields.Selection(
        [("global", "Global"), ("branch", "Per Branch"), ("role", "Per Role")],
        default="global", required=True)
    branch_ids = fields.Many2many("fix.branch", string="Enabled Branches",
                                  help="Only used when scope=branch")
    role_ids = fields.Many2many("fix.role", string="Enabled Roles",
                                help="Only used when scope=role (M29 fix.role)")
    default_for_new = fields.Boolean(default=False,
                                     help="If True, new branches/roles get this flag enabled")

    @api.model
    def is_enabled(self, key: str, branch=None, role=None) -> bool:
        """Check if a feature flag is enabled for the given context.

        Fail-closed: an unknown key returns False (the safe default).
        """
        flag = self.sudo().search([("key", "=", key), ("active", "=", True)], limit=1)
        if not flag:
            _logger.debug("feature flag %s not found — defaulting to disabled", key)
            return False
        if not flag.enabled:
            return False
        if flag.scope == "global":
            return True
        if flag.scope == "branch" and branch:
            return branch in flag.branch_ids
        if flag.scope == "role" and role:
            return role in flag.role_ids
        # scope is set but no context provided — fail closed
        return False


def flag_enabled(key: str, default: bool = False):
    """Decorator: gate a method behind a feature flag (OPS-06).

    Usage:
        @flag_enabled("dispatch.auto_assign")
        def _auto_assign(self): ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            flag_model = self.env["fix.feature.flag"]
            if not flag_model.is_enabled(key):
                if default:
                    return func(self, *args, **kwargs)
                return None  # silently disabled — the safe default
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
