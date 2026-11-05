# fix.feature.flag — the feature-flag service (P03-M04-T05, OPS-06/EP-07).
# Every capability from Wave 1 onward ships behind a flag.
# Usage: @flag_enabled("my_feature_key") — decorator checks this model.
import functools
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_entity import require_platform_admin

_logger = logging.getLogger(__name__)

# A12 P2 / M30-9 wiring registry — see create() below. One entry ships with
# the contract itself: the SLA auto-escalation kill switch (cd_itsm reads it
# with is_disabled; presence-based opt-out, so the audit-mandated escalation
# keeps running until an operator switches it off explicitly).
FLAG_WIRED_KEYS = {"itsm.sla_auto_escalate"}


class FixFeatureFlag(models.Model):
    """A feature flag: any new capability is disableable without deployment."""

    _name = "fix.feature.flag"
    _description = "Feature Flag"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _key_unique = models.Constraint("UNIQUE (key)", "Feature flag key must be unique")

    key = fields.Char(
        string="Key",
        required=True,
        index=True,
        help="Dot-notation key, e.g. 'dispatch.auto_assign'",
    )
    name = fields.Char(string="Description", required=True)
    enabled = fields.Boolean(
        default=False, tracking=True, help="False = capability disabled (safe default)"
    )
    scope = fields.Selection(
        [("global", "Global"), ("branch", "Per Branch"), ("role", "Per Role")],
        default="global",
        required=True,
    )
    branch_ids = fields.Many2many(
        "fix.branch", string="Enabled Branches", help="Only used when scope=branch"
    )
    # role_ids (fix.role) lives in cd_rbac_ext — the PLATFORM layer cannot
    # reference M29's model (live-install finding: unknown comodel at registry
    # load). scope="role" fails CLOSED here; cd_rbac_ext overrides is_enabled
    # to make role scoping work where fix.role exists.
    default_for_new = fields.Boolean(
        default=False, help="If True, new branches/roles get this flag enabled"
    )

    # A12 X4: toggling a flag flips live capability (the 60-second kill
    # switch, BRU-ADM-09/10), so the register is Platform Admin master data.
    # is_enabled stays fail-closed for every reader — a missing or unreadable
    # flag answers False, never True.
    #
    # A12 P2 / M30-9 (feature flags gate no code): a flag may exist ONLY for
    # a capability the code actually reads. FLAG_WIRED_KEYS is the wiring
    # registry — a key lands here the moment @flag_enabled / is_disabled()
    # references it, and create/write refuse every other key. The register
    # can no longer hold decorative flags; the "kill switch" claim is true
    # for every row in the table.
    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The feature-flag register")
        unknown = {v.get("key") for v in vals_list} - FLAG_WIRED_KEYS
        if unknown and not self.env.su:
            raise UserError(
                "No code reads a flag keyed %s. Wire the capability first "
                "(@flag_enabled / is_disabled in FLAG_WIRED_KEYS) or do not "
                "register the flag." % ", ".join(sorted(k or "?" for k in unknown))
            )
        return super().create(vals_list)

    def write(self, vals):
        require_platform_admin(self.env, "The feature-flag register")
        if "key" in vals and vals["key"] not in FLAG_WIRED_KEYS and not self.env.su:
            raise UserError(
                "No code reads a flag keyed %s. Wire the capability first "
                "(@flag_enabled / is_disabled in FLAG_WIRED_KEYS) or do not "
                "register the flag." % vals["key"]
            )
        return super().write(vals)

    def unlink(self):
        require_platform_admin(self.env, "The feature-flag register")
        return super().unlink()

    @api.model
    def is_enabled(self, key: str, branch=None, role=None) -> bool:
        """Check if a feature flag is enabled for the given context.

        Fail-closed: an unknown key returns False (the safe default).
        """
        # fix.feature.flag carries no `active` field: filtering on it raised
        # ValueError on every check (and on every @flag_enabled call).
        flag = self.sudo().search([("key", "=", key)], limit=1)
        if not flag:
            _logger.debug("feature flag %s not found — defaulting to disabled", key)
            return False
        if not flag.enabled:
            return False
        if flag.scope == "global":
            return True
        if flag.scope == "branch" and branch:
            return branch in flag.branch_ids
        # scope is set but no context provided (or role scope, which only
        # cd_rbac_ext understands) — fail closed
        return False

    @api.model
    def is_disabled(self, key: str) -> bool:
        """Kill-switch read: True only when the flag EXISTS and is disabled.

        The opt-out twin of is_enabled (opt-in, fail-closed): an automated
        control an audit mandates — e.g. SLA escalation — runs by DEFAULT and
        is switched OFF explicitly, never the reverse. A missing row means
        the default behaviour (on); is_enabled's missing row means off.
        """
        return bool(self.sudo().search([("key", "=", key), ("enabled", "=", False)], limit=1))


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
