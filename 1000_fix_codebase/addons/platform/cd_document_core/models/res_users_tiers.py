# res_users_tiers — A10 deep audit (2026-11-22, A2-F03): the confidentiality
# tier field on fix.document promised "the minimum isolation tier required to
# READ this document", but nothing enforced it — a T3 (role-scoped) or T5
# (residency-classified) document was readable by any internal user of the
# company/OU.
#
# The gate is QUERY-TIME: a domain appended in fix.document._search and in
# _check_access (the Odoo 19 hook that read/write/unlink enforce through), NOT
# an ir.rule: Odoo caches rule domains per user (ir.rule._compute_domain is
# ormcached on env.uid), so a tier granted by a role assignment stayed
# invisible until a cache clear — the rule looked right and behaved stale.
#
# The tier codes a user may read come from the M29 register
# (fix.isolation.tier role grants, reached through the user's ACTIVE role
# assignments). T0/T1 are the every-employee tiers by the register's own
# definition (T1 = "internal (all employees)"), so they are always in the
# set. The lifecycle officers (Records/Controller) and system administrators
# read across tiers: the register governs what THEY may do with a classified
# document (hold, release, dispose), not whether the row exists for them.
#
# cd_document_core does not depend on cd_rbac_ext: the register is read
# through env.get and the gate degrades to T0/T1 where it is absent.
import functools

from odoo import api, fields, models
from odoo.osv import expression

_INTERNAL_TIERS = ("T0", "T1", "T2")  # T2 is OU-scoped by its own rule; the tier GATE covers T3-T5
_PRIVILEGED_GROUPS = (
    "base.group_system",
    "cd_document_core.group_document_records",
    "cd_document_core.group_document_controller",
)


class ResUsersDocumentTiers(models.Model):
    _inherit = "res.users"

    fix_document_tier_codes = fields.Char(
        compute="_compute_fix_document_tier_codes",
        help="The confidentiality tiers (T0-T5) this user may read, per the M29 "
        "isolation-tier register and the user's active role assignments.",
    )

    def _compute_fix_document_tier_codes(self):
        for rec in self:
            codes = rec._fix_document_tier_codes()
            rec.fix_document_tier_codes = (
                ",".join(sorted(codes))
                if codes is not None
                else ",".join(sorted((*_INTERNAL_TIERS, "T3", "T4", "T5")))
            )

    def _fix_document_tier_codes(self):
        """The tier codes this user may read; None = unrestricted (officer)."""
        for gid in _PRIVILEGED_GROUPS:
            if self.env.ref(gid, raise_if_not_found=False) is not None and self.has_group(gid):
                return None
        codes = set(_INTERNAL_TIERS)
        Tier = self.env.get("fix.isolation.tier")
        Assignment = self.env.get("fix.role.assignment")
        if Tier is not None and Assignment is not None:
            roles = (
                Assignment.sudo()
                .search([("user_id", "in", self.ids), ("ended_on", "=", False)])
                .mapped("role_id")
            )
            if roles:
                codes |= set(Tier.sudo().search([("role_ids", "in", roles.ids)]).mapped("code"))
        return codes


class FixDocumentTierGate(models.Model):
    """The confidentiality read gate, at query time."""

    _inherit = "fix.document"

    @api.model
    def _fix_tier_gate_domain(self):
        if self.env.su:
            return []
        codes = self.env.user._fix_document_tier_codes()
        if codes is None:
            return []
        # the creator keeps sight of what they filed (the capture clerk
        # raises the tier, then must still see the exception to fix it)
        return [
            "|",
            "|",
            ("isolation_tier", "=", False),
            ("isolation_tier", "in", sorted(codes)),
            ("create_uid", "=", self.env.user.id),
        ]

    @api.model
    def _search(
        self,
        domain,
        offset=0,
        limit=None,
        order=None,
        *,
        active_test=True,
        bypass_access=False,
    ):
        if not bypass_access:
            gate = self._fix_tier_gate_domain()
            if gate:
                domain = expression.AND([domain, gate])
        return super()._search(
            domain,
            offset=offset,
            limit=limit,
            order=order,
            active_test=active_test,
            bypass_access=bypass_access,
        )

    def _check_access(self, operation):
        """read/write/unlink on records already held: the same gate, checked
        against the actual records (Odoo 19 funnels these through this hook;
        the ir.rule domain it also consults is cached per user, so the gate
        is re-asserted here)."""
        result = super()._check_access(operation)
        if result is not None or operation == "create":
            return result
        gate = self._fix_tier_gate_domain()
        if not gate:
            return None
        allowed = self.sudo().with_context(active_test=False).filtered_domain(gate)
        forbidden = self - allowed
        if forbidden:
            Rule = self.env["ir.rule"]
            return forbidden, functools.partial(Rule._make_access_error, operation, forbidden)
        return None
