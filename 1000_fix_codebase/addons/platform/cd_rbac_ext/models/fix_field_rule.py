# fix.field.rule - field-level permission rules (P03-M02-T05).
#
# Where they apply (A12 finish, E28): on the P03 workspace read path, in lists and
# forms (controllers/p03_generic_api.py). hidden strips the field; masked shows ***.
# fix.sensitive.field masking rules apply on the same path. They are NOT applied to
# the Odoo ORM or web client, to report packs, or to exports: those keep their own
# ACLs. A caller is cleared by base.group_system, by the Sensitive Data Clearance
# group, or for one field by holding a role named on a read/write rule for it.
import hashlib

from odoo import api, fields, models
from odoo.exceptions import ValidationError

CLEARANCE_GROUPS = ("base.group_system", "cd_rbac_ext.group_sensitive_data_clearance")


def mask_value(value, how):
    """One value as an uncleared caller sees it. Empty stays empty, because an
    empty field gives nothing away and the screen should still look empty."""
    if value in (None, False, ""):
        return value
    if isinstance(value, dict):  # many2one {id,name} or selection {key,label} from the list path
        value = value.get("name") or value.get("label") or value.get("key") or ""
    text = str(value)
    if how == "last4":
        return "***%s" % text[-4:]
    if how == "hash":
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return "***"


class FixModelRefMixin(models.AbstractModel):
    """Lets a form name a model or field by technical name. ir.model has 1,386 rows
    and ir.model.fields 39,636: a dropdown offering the first 300 cannot reach most
    of them (E27)."""

    _name = "fix.model.ref.mixin"
    _description = "Model and Field Reference by Technical Name"

    @api.model
    def _fix_resolve_refs(self, vals):
        model_name = (vals.pop("fix_model_name", "") or "").strip()
        field_name = (vals.pop("fix_field_name", "") or "").strip()
        if model_name:
            model = self.env["ir.model"].sudo().search([("model", "=", model_name)], limit=1)
            if not model:
                raise ValidationError("There is no model named %s." % model_name)
            vals["model_id"] = model.id
        if field_name:
            model_id = vals.get("model_id") or (self.model_id.id if self else False)
            field = (
                self.env["ir.model.fields"]
                .sudo()
                .search([("model_id", "=", model_id), ("name", "=", field_name)], limit=1)
            )
            if not field:
                raise ValidationError("This model has no field named %s." % field_name)
            vals["field_id"] = field.id
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        return super().create([self._fix_resolve_refs(dict(vals)) for vals in vals_list])

    def write(self, vals):
        return super().write(self._fix_resolve_refs(dict(vals)))


class FixFieldRule(models.Model):
    """One field, one permission, for a set of roles. An empty role list applies the
    rule to every caller who is not cleared."""

    _name = "fix.field.rule"
    _description = "Field-Level Permission Rule"
    _inherit = ["fix.model.ref.mixin"]
    _order = "model_id, field_id"

    model_id = fields.Many2one("ir.model", string="Model", required=True, ondelete="cascade")
    field_id = fields.Many2one("ir.model.fields", string="Field", required=True, ondelete="cascade")
    fix_model_name = fields.Char(
        string="Model (technical name)", compute="_compute_ref_names", readonly=False
    )
    fix_field_name = fields.Char(
        string="Field (technical name)", compute="_compute_ref_names", readonly=False
    )
    role_ids = fields.Many2many(
        "fix.role", string="Roles", help="Empty = applies to every caller who is not cleared"
    )
    permission = fields.Selection(
        [
            ("read", "Read Only"),
            ("write", "Read + Write"),
            ("hidden", "Hidden"),
            ("masked", "Masked (shows ***)"),
        ],
        default="hidden",
        required=True,
        help="On the P03 workspace: hidden strips the field from lists and forms, masked shows "
        "***. read/write name the roles that stay cleared for this field.",
    )
    operating_unit_ids = fields.Many2many(
        "operating.unit", string="Scope (OUs)", help="Empty = all OUs"
    )
    active = fields.Boolean(default=True)

    @api.depends("model_id", "field_id")
    def _compute_ref_names(self):
        for rec in self:
            rec.fix_model_name = rec.model_id.model
            rec.fix_field_name = rec.field_id.name

    def _fix_applies_to(self, user, held):
        """This rule, for this caller: its roles and its OU scope."""
        self.ensure_one()
        if self.role_ids and not (self.role_ids & held):
            return False
        if self.operating_unit_ids and "assigned_operating_unit_ids" in user._fields:
            return bool(self.operating_unit_ids & user.assigned_operating_unit_ids)
        return True

    @api.model
    def _fix_read_policy(self, model_name, field_names):
        """{field: hidden | full | last4 | hash} for the calling user on the P03 read
        path. Empty for a cleared caller. Read-only: runs on read-only routes."""
        if self.env.su or not field_names:
            return {}
        user = self.env.user
        if any(user.has_group(group) for group in CLEARANCE_GROUPS):
            return {}
        names = set(field_names)
        rules = self.sudo().search(
            [("model_id.model", "=", model_name), ("field_id.name", "in", sorted(names))]
        )
        sensitive = (
            self.env["fix.sensitive.field"]
            .sudo()
            .search(
                [
                    ("model_name", "=", model_name),
                    ("field_name", "in", sorted(names)),
                    ("masking_rule", "!=", "none"),
                    ("company_id", "in", self.env.companies.ids),
                ]
            )
        )
        if not rules and not sensitive:
            return {}
        held = self.env["fix.sod.control"].user_held_roles(user)
        real_user = user.sudo()
        policy = {}
        cleared = set()
        for rule in rules:
            if not rule._fix_applies_to(real_user, held):
                continue
            if rule.permission in ("read", "write"):
                if rule.role_ids:
                    cleared.add(rule.field_id.name)
            elif rule.permission == "hidden":
                policy[rule.field_id.name] = "hidden"
            else:
                policy.setdefault(rule.field_id.name, "full")
        for row in sensitive:
            policy.setdefault(row.field_name, row.masking_rule)
        return {name: how for name, how in policy.items() if name not in cleared}

    @api.model
    def _fix_apply_policy(self, row, policy):
        """Apply a _fix_read_policy result to one row of served values."""
        for name, how in policy.items():
            if name not in row:
                continue
            if how == "hidden":
                row.pop(name)
            else:
                row[name] = mask_value(row[name], how)
        return row


class FixFieldRuleDisplayRoll(models.Model):
    """Read-only role-name roll for the D365 Field Rule form (M29 wiring
    pass, 2026-11-05)."""

    _inherit = "fix.field.rule"
    _description = "Fix Field Rule M29 Display Roll"

    fix_role_roll = fields.Char(
        string="Roles",
        compute="_compute_display_rolls",
        help="The roles this field rule applies to; empty means every caller who is not "
        "cleared.",
    )

    def _compute_display_rolls(self):
        for rec in self:
            codes = rec.role_ids.mapped("code")
            rec.fix_role_roll = ", ".join(sorted(codes)) if codes else "All uncleared callers"


class IrRuleModelRef(models.Model):
    _name = "ir.rule"
    _inherit = ["ir.rule", "fix.model.ref.mixin"]

    fix_model_name = fields.Char(
        string="Model (technical name)", compute="_compute_fix_model_name", readonly=False
    )

    @api.depends("model_id")
    def _compute_fix_model_name(self):
        for rec in self:
            rec.fix_model_name = rec.model_id.model


class IrModelAccessModelRef(models.Model):
    _name = "ir.model.access"
    _inherit = ["ir.model.access", "fix.model.ref.mixin"]

    fix_model_name = fields.Char(
        string="Model (technical name)", compute="_compute_fix_model_name", readonly=False
    )

    @api.depends("model_id")
    def _compute_fix_model_name(self):
        for rec in self:
            rec.fix_model_name = rec.model_id.model
