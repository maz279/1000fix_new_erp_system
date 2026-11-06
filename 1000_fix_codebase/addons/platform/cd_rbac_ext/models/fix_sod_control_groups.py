# fix.sod.control — the A08 S4 group-pair extension (B6, 2026-11-04).
#
# Loaded AFTER fix_sod_control.py: Odoo merges same-_name classes, so this
# file ADDS the Odoo-group-pair controls (the finance duty rule set,
# data/fix_sod_finance_controls.xml) and the grant-path engine the hooks in
# fix_sod_grant_hooks.py call, while the A12 R2 gates (check_user_assignment,
# gate_role_set, check_role_set, ...) defined in the base file stay live.
#
# A08 S4 / A12 R2 (M29-4): a control pairs two ROLES (the SP-006 register) or
# two Odoo GROUPS (the finance duty rule set). The check runs at every grant
# path (res.users / res.groups writes, the access request grant, the JML
# apply, hr.employee role assignment, certification): a change that CREATES a
# conflicting combination is refused unless an approved, unexpired exception
# (fix.sod.mitigation, FR-SEC-024) covers that user and control. Existing
# conflicts are never blocked by an unrelated change; they are listed by
# `fix_report_violations()`.
import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class FixSodControlGroups(models.Model):
    """The group-pair fields and the grant-path SoD engine (A08 S4)."""

    _inherit = "fix.sod.control"

    control_type = fields.Selection(
        [("role", "Role pair (SP-006 register)"), ("group", "Odoo group pair (duty)")],
        string="Pairs",
        default="role",
        required=True,
        help="role = two fix.role rows; group = two Odoo res.groups (named by XML ID so a "
        "control can name a group of an addon that loads after this one).",
    )
    group_a_xmlid = fields.Char(
        string="Group A (XML ID)", help="e.g. account.group_account_user; resolved at check time"
    )
    group_b_xmlid = fields.Char(string="Group B (XML ID)")
    group_a_id = fields.Many2one(
        "res.groups", string="Group A", ondelete="cascade", help="Overrides Group A (XML ID)"
    )
    group_b_id = fields.Many2one(
        "res.groups", string="Group B", ondelete="cascade", help="Overrides Group B (XML ID)"
    )
    pair_label = fields.Char(string="Pair", compute="_compute_pair_label")
    measurable = fields.Boolean(
        compute="_compute_pair_label",
        help="False when the pair cannot be told apart by group membership: a group is not "
        "installed, both sides are the same group, or a role's group is shared with another "
        "role (M29-4). Role pairs are still enforced on explicit role assignments.",
    )

    @api.depends(
        "control_type",
        "role_a_id",
        "role_b_id",
        "group_a_id",
        "group_b_id",
        "group_a_xmlid",
        "group_b_xmlid",
    )
    def _compute_pair_label(self):
        unique = self._fix_unique_role_groups()
        for rec in self:
            if rec.control_type == "group":
                ga, gb = rec._fix_group_side("a"), rec._fix_group_side("b")
                rec.pair_label = "%s × %s" % (
                    ga.display_name if ga else "%s (not installed)" % (rec.group_a_xmlid or "?"),
                    gb.display_name if gb else "%s (not installed)" % (rec.group_b_xmlid or "?"),
                )
            else:
                rec.pair_label = "%s × %s" % (rec.role_a_id.code or "?", rec.role_b_id.code or "?")
            rec.measurable = bool(rec._fix_pair_groups(unique))

    @api.constrains("control_type", "role_a_id", "role_b_id")
    def _check_different_roles(self):
        for rec in self:
            if rec.control_type != "role":
                continue
            if not (rec.role_a_id and rec.role_b_id):
                raise ValidationError("A role-pair SoD control needs both Role A and Role B.")
            if rec.role_a_id == rec.role_b_id:
                raise ValidationError("SoD control cannot reference the same role twice.")

    @api.constrains("control_type", "group_a_id", "group_b_id", "group_a_xmlid", "group_b_xmlid")
    def _check_group_pair(self):
        for rec in self:
            if rec.control_type != "group":
                continue
            if not (
                (rec.group_a_id or rec.group_a_xmlid) and (rec.group_b_id or rec.group_b_xmlid)
            ):
                raise ValidationError("A group-pair SoD control needs both Group A and Group B.")
            ga, gb = rec._fix_group_side("a"), rec._fix_group_side("b")
            same_xmlid = (
                not rec.group_a_id
                and not rec.group_b_id
                and rec.group_a_xmlid.strip() == rec.group_b_xmlid.strip()
            )
            if same_xmlid or (ga and gb and ga == gb):
                raise ValidationError("SoD control cannot reference the same group twice.")

    # ------------------------------------------------------------------
    # Pair resolution
    # ------------------------------------------------------------------
    def _fix_group_side(self, side):
        self.ensure_one()
        group = self[f"group_{side}_id"]
        if group:
            return group.sudo()
        xmlid = (self[f"group_{side}_xmlid"] or "").strip()
        found = self.env.ref(xmlid, raise_if_not_found=False) if "." in xmlid else None
        if not found or found._name != "res.groups":
            return self.env["res.groups"].sudo()
        return found.sudo()

    @api.model
    def _fix_unique_role_groups(self):
        """Group ids that exactly one active role maps to (so membership names the role)."""
        counts = {}
        for role in self.env["fix.role"].sudo().search([("group_id", "!=", False)]):
            counts[role.group_id.id] = counts.get(role.group_id.id, 0) + 1
        return {gid for gid, n in counts.items() if n == 1}

    def _fix_pair_groups(self, unique=None):
        """(group_a, group_b) whose joint membership IS the conflict, or None."""
        self.ensure_one()
        if self.control_type == "group":
            ga, gb = self._fix_group_side("a"), self._fix_group_side("b")
        else:
            if unique is None:
                unique = self._fix_unique_role_groups()
            ga, gb = self.role_a_id.group_id.sudo(), self.role_b_id.group_id.sudo()
            if ga.id not in unique or gb.id not in unique:
                return None
        if not ga or not gb or ga == gb:
            return None
        return ga, gb

    @api.model
    def _fix_index(self):
        """Every active control with its resolved pair, computed once per check."""
        unique = self._fix_unique_role_groups()
        index = []
        for control in self.sudo().search([("active", "=", True)]):
            index.append((control, control._fix_pair_groups(unique)))
        return {"controls": index, "unique": unique}

    # ------------------------------------------------------------------
    # Holdings and conflicts
    # ------------------------------------------------------------------
    @api.model
    def _fix_held_roles(self, user=None, employees=None, groups=None, unique=None):
        """Roles a person holds: by a group that identifies the role, by a granted
        access request, or as an employee's primary / additional role."""
        Role = self.env["fix.role"].sudo()
        held = Role.browse()
        if groups:
            if unique is None:
                unique = self._fix_unique_role_groups()
            gids = [gid for gid in groups.ids if gid in unique]
            if gids:
                held |= Role.search([("group_id", "in", gids)])
        if user:
            held |= (
                self.env["fix.access.request"]
                .sudo()
                .search(
                    [
                        ("user_id", "=", user.id),
                        ("state", "=", "granted"),
                        ("request_type", "in", ("grant", "elevate")),
                    ]
                )
                .mapped("role_id")
            )
        for emp in employees or []:
            emp = emp.sudo()
            if "primary_role_id" in emp._fields:
                held |= emp.primary_role_id
            if "additional_role_ids" in emp._fields:
                held |= emp.additional_role_ids
        return held

    @api.model
    def _fix_user_employees(self, user):
        if not user or "hr.employee" not in self.env:
            return None
        return (
            self.env["hr.employee"]
            .sudo()
            .with_context(active_test=False)
            .search([("user_id", "=", user.id)])
        )

    @api.model
    def _fix_conflicts(
        self, user=None, employees=None, extra_groups=None, extra_roles=None, index=None
    ):
        """The active controls a person violates (optionally after gaining
        `extra_groups` / `extra_roles`). `user` may be empty for an employee
        without a login (role pairs only)."""
        if index is None:
            index = self._fix_index()
        groups = self.env["res.groups"].sudo()
        if user:
            user = user.sudo()
            user.invalidate_recordset(["group_ids", "all_group_ids"])
            groups = user.with_context(active_test=False).all_group_ids
        if extra_groups:
            groups |= extra_groups.sudo().all_implied_ids
        if extra_roles:
            for role in extra_roles.sudo():
                if role.group_id:
                    groups |= role.group_id.all_implied_ids
        if employees is None:
            employees = self._fix_user_employees(user)
        roles = self._fix_held_roles(
            user=user, employees=employees, groups=groups, unique=index["unique"]
        )
        if extra_roles:
            roles |= extra_roles.sudo()
        # A business role carries its mapped group's duties even before the group is
        # provisioned (an M21 role assignment writes the role, not the group).
        groups |= roles.mapped("group_id").all_implied_ids
        violated = self.browse()
        for control, pair in index["controls"]:
            if control.control_type == "role":
                if control.role_a_id in roles and control.role_b_id in roles:
                    violated |= control
            elif pair and pair[0] in groups and pair[1] in groups:
                violated |= control
        return violated

    @api.model
    def _fix_enforce(self, user, before, after, path, strict=False, employees=None):
        """Refuse the NEW conflicts (after - before) that no approved, unexpired
        exception covers. Superuser / data loading passes but is logged, unless
        `strict` (the explicit workflow grant paths check whoever calls them)."""
        new = (after - before).sudo()
        if not new:
            return True
        refused = self.browse()
        notes = []
        Mitigation = self.env["fix.sod.mitigation"].sudo()
        for control in new:
            if control.conflict_action == "log":
                notes.append("%s logged (log-only control)" % control.code)
                continue
            waiver = Mitigation._fix_valid_for(control, user) if user else Mitigation
            if waiver:
                notes.append("%s allowed under exception %s" % (control.code, waiver[0].name))
                continue
            refused |= control
        if refused and self.env.su and not strict:
            notes.append(
                "%s allowed: superuser / data-loading grant" % ", ".join(refused.mapped("code"))
            )
            refused = self.browse()
        if refused:
            who = user.login if user else ", ".join(e.name for e in (employees or [])) or "?"
            raise ValidationError(
                "Segregation of duties: this change (%s) would give %s an incompatible "
                "combination. %s. Request a time-boxed SoD exception with a mitigating "
                "control, approved by someone other than the grantee (FR-SEC-024), or "
                "give the duty to another person."
                % (
                    path,
                    who,
                    "; ".join(
                        "SoD control %s: %s (%s)" % (c.code, c.name, c.pair_label) for c in refused
                    ),
                )
            )
        for note in notes:
            self._fix_log_sod_event(user, path, note)
        return True

    @api.model
    def _fix_log_sod_event(self, user, path, note):
        detail = ("SoD %s: %s" % (path, note))[:250]
        _logger.warning("M29 SoD: user %s - %s", user.login if user else "?", detail)
        self.env["fix.security.audit"].sudo().create(
            {
                "event": "privileged",
                "object_ref": ("res.users,%s" % user.id) if user else "hr.employee",
                "detail": detail,
            }
        )

    # ------------------------------------------------------------------
    # Detective: the standing violation report (FR-SEC-024 quarterly report)
    # ------------------------------------------------------------------
    @api.model
    def fix_report_violations(self):
        """Every active user's current conflicts, mitigated or not, plus the
        controls that cannot be measured by group membership. Read-only."""
        Mitigation = self.env["fix.sod.mitigation"].sudo()
        index = self._fix_index()
        rows = []
        for user in self.env["res.users"].sudo().search([("active", "=", True)]):
            for control in self._fix_conflicts(user=user, index=index):
                waiver = Mitigation._fix_valid_for(control, user)
                rows.append(
                    {
                        "control": control.code,
                        "name": control.name,
                        "pair": control.pair_label,
                        "action": control.conflict_action,
                        "user_id": user.id,
                        "login": user.login,
                        "mitigated": bool(waiver),
                        "exception": waiver[0].name if waiver else False,
                        "exception_until": str(waiver[0].valid_until) if waiver else False,
                    }
                )
        unmeasurable = [
            {"control": c.code, "name": c.name, "pair": c.pair_label}
            for c, pair in index["controls"]
            if not pair
        ]
        return {
            "violations": rows,
            "unmitigated": len([r for r in rows if not r["mitigated"]]),
            "unmeasurable": unmeasurable,
        }
