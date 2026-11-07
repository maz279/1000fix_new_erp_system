# M29 access-posture display fields (workspace wiring pass, 2026-11-05).
#
# WHY. The governance engine already measures everything a top-class ERP
# shows on a user master record — resolved business roles, the DOFA tier,
# security authority appointments, workspace access, the last certification
# decision and open access requests — but none of it was VISIBLE on the
# res.users surface, so the D365 User form looked empty while the backend
# was complete.
#
# These fields are READ-ONLY COMPUTES. They change nothing: the only write
# path for entitlements stays the approved access request (X1) and the JML
# chain, and the SoD gate on res.users.group_ids writes still applies
# (res_users_ext.py). Each compute reads the real registers — nothing is
# estimated, and a register with no rows renders as "—".
#
# The m2m NAME ROLLS (fix.role / fix.field.rule / fix.isolation.tier) serve
# the same purpose for many2many fields the workspace form cannot edit:
# visibility without a parallel permission system.
from odoo import api, fields, models

# The P03 workspace gates (security/fix_role_groups.xml) — display names of
# the workspace groups a user may hold.
WORKSPACE_GROUPS = [
    ("group_ws_front_desk", "Service Intake"),
    ("group_ws_service_orders", "Service Orders"),
    ("group_ws_party_master", "Party Master"),
    ("group_ws_devices", "Device Registry"),
    ("group_ws_catalogue", "Catalogue"),
    ("group_ws_administration", "Administration"),
]

# The A12 X1/R5 authority appointments (ship empty; business appointments).
AUTHORITY_GROUPS = [
    ("group_access_approver", "Access Approver"),
    ("group_key_custodian", "Key Custodian"),
]

# cd_entity_config DOFA tier groups, lowest → highest (fix_dofa.TIER_GROUP).
DOFA_TIER_GROUPS = [
    ("group_dofa_tier_1", "Tier 1 — Team Lead / Supervisor"),
    ("group_dofa_tier_2", "Tier 2 — Branch / Operations Manager"),
    ("group_dofa_tier_3", "Tier 3 — CX / Commercial Director"),
    ("group_dofa_tier_4", "Tier 4 — CFO / CCO / COO"),
    ("group_dofa_tier_5", "Tier 5 — Managing Director / Board"),
]


class ResUsersAccessPosture(models.Model):
    """Read-only access-posture panels for the M29 D365 User form."""

    _inherit = "res.users"
    _description = "Res Users M29 Access Posture"

    # ---- entitlement (measured through the role->group mapping) ----------

    fix_role_codes = fields.Char(
        string="Business Roles Held",
        compute="_compute_access_posture",
        help="The fix.role codes this user holds: what was assigned, what the employee master "
        "records, and groups that name one role (the same resolution the Access Review pack "
        "reports). Granted only through approved access requests / JML — never typed.",
    )
    fix_role_count = fields.Integer(string="Roles Held", compute="_compute_access_posture")
    fix_group_names = fields.Char(
        string="Permission Groups",
        compute="_compute_access_posture",
        help="Every Odoo group the user holds, as a read-only roll-up. "
        "Group membership changes only through the approved access paths.",
    )
    fix_allowed_companies = fields.Char(
        string="Allowed Companies",
        compute="_compute_access_posture",
        help="The companies whose data the user may see (res.users.company_ids).",
    )
    fix_workspaces = fields.Char(
        string="Workspace Access",
        compute="_compute_access_posture",
        help="The P03 workspaces the user may enter (the workspace groups "
        "they hold; a workspace they cannot enter does not appear — NVR-22).",
    )

    # ---- authority -------------------------------------------------------

    fix_dofa_tier = fields.Char(
        string="DOFA Tier Held",
        compute="_compute_access_posture",
        help="The highest Delegation of Financial Authority tier group the "
        "user holds. Threshold amounts are NOT per-user: they live in the "
        "two-person-ruled DOFA ladders (M30).",
    )
    fix_authority = fields.Char(
        string="Security Authority",
        compute="_compute_access_posture",
        help="M29 authority appointments held: Access Approver and/or Key "
        "Custodian. Both groups ship empty; appointments are business "
        "decisions recorded as approved access requests.",
    )
    fix_approver_groups = fields.Char(
        string="Approver Appointments",
        compute="_compute_access_posture",
        help="Other held groups whose role is an approver or custodian "
        "appointment (e.g. Counter Refund Approver, Trade-In Payout "
        "Approver) — measured by group name, shown read-only.",
    )

    # ---- lifecycle -------------------------------------------------------

    fix_last_certification = fields.Char(
        string="Last Certification",
        compute="_compute_access_posture",
        help="The most recent access-certification line for this user "
        "(period: decision). Unconfirmed lines are auto-revoked past their "
        "due date (FR-SEC-026 close-out cron).",
    )
    fix_open_requests = fields.Integer(
        string="Open Access Requests",
        compute="_compute_access_posture",
        help="Access requests for this user still submitted or approved "
        "(not yet granted, rejected or revoked).",
    )

    # ------------------------------------------------------------------

    def _fix_may_see_posture(self):
        """E25: someone's permission groups and DOFA tier are not for every
        colleague: the user himself, Access Rights admins and Access Approvers."""
        viewer = self.env.user
        return (
            self.env.su
            or viewer == self
            or viewer.has_group("base.group_erp_manager")
            or viewer.has_group("cd_rbac_ext.group_access_approver")
        )

    @api.depends_context("uid")
    def _compute_access_posture(self):
        Cert = self.env.get("fix.access.certification")
        Request = self.env.get("fix.access.request")
        Sod = self.env.get("fix.sod.control")
        for user in self:
            if not user._fix_may_see_posture():
                user.update(
                    {
                        "fix_role_codes": False,
                        "fix_role_count": 0,
                        "fix_group_names": False,
                        "fix_allowed_companies": False,
                        "fix_workspaces": False,
                        "fix_dofa_tier": False,
                        "fix_authority": False,
                        "fix_approver_groups": False,
                        "fix_last_certification": False,
                        "fix_open_requests": 0,
                    }
                )
                continue
            groups = user.sudo().group_ids
            group_ids = set(groups.ids)

            # entitlement ------------------------------------------------
            # NOTE: env.get() returns an EMPTY RECORDSET (falsy) for a loaded
            # model, None only when absent — guard with `is not None`.
            roles = Sod.user_held_roles(user) if Sod is not None else self.env["fix.role"]
            codes = sorted(roles.mapped("code"))
            user.fix_role_codes = ", ".join(codes) if codes else "—"
            user.fix_role_count = len(codes)
            names = sorted(groups.mapped("name"))
            user.fix_group_names = ", ".join(names) if names else "—"
            companies = sorted(user.sudo().company_ids.mapped("name"))
            user.fix_allowed_companies = ", ".join(companies) if companies else "—"

            workspaces = [
                label
                for xmlid, label in WORKSPACE_GROUPS
                if self.env.ref("cd_rbac_ext.%s" % xmlid, raise_if_not_found=False)
                and self.env.ref("cd_rbac_ext.%s" % xmlid).id in group_ids
            ]
            user.fix_workspaces = ", ".join(workspaces) if workspaces else "—"

            # authority --------------------------------------------------
            tier_label = "—"
            for xmlid, label in DOFA_TIER_GROUPS:
                ref = self.env.ref("cd_entity_config.%s" % xmlid, raise_if_not_found=False)
                if ref and ref.id in group_ids:
                    tier_label = label  # last (highest) wins
            user.fix_dofa_tier = tier_label

            authority = [
                label
                for xmlid, label in AUTHORITY_GROUPS
                if self.env.ref("cd_rbac_ext.%s" % xmlid, raise_if_not_found=False)
                and self.env.ref("cd_rbac_ext.%s" % xmlid).id in group_ids
            ]
            user.fix_authority = ", ".join(authority) if authority else "—"

            authority_ids = {
                self.env.ref("cd_rbac_ext.%s" % x, raise_if_not_found=False).id
                for x, _ in AUTHORITY_GROUPS
            }
            approvers = sorted(
                g.name
                for g in groups
                if g.id not in authority_ids
                and ("Approver" in (g.name or "") or "Custodian" in (g.name or ""))
            )
            user.fix_approver_groups = ", ".join(approvers) if approvers else "—"

            # lifecycle --------------------------------------------------
            if Cert is not None:
                last = Cert.sudo().search(
                    [("user_id", "=", user.id)], order="period desc, id desc", limit=1
                )
                if last:
                    decision = dict(type(last)._fields["decision"].selection).get(
                        last.decision, last.decision
                    )
                    user.fix_last_certification = "%s: %s" % (last.period, decision)
                else:
                    user.fix_last_certification = "Never reviewed"
            else:
                user.fix_last_certification = "—"
            if Request is not None:
                user.fix_open_requests = Request.sudo().search_count(
                    [
                        ("user_id", "=", user.id),
                        ("state", "in", ("submitted", "approved")),
                    ]
                )
            else:
                user.fix_open_requests = 0


# The m2m NAME ROLLS for fix.role / fix.field.rule / fix.isolation.tier live
# in their base model files (fix_role.py, fix_field_rule.py,
# fix_isolation_tier.py). A separate file inheriting them breaks when ruff
# isort sorts it before the base definition — an _inherit of a not-yet-loaded
# model raises "does not exist in registry" at startup. res.users (above) is
# a base model, so this file's import position is safe.
