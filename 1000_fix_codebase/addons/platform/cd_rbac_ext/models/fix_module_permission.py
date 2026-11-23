# M29 per-module permissions (capture audit 2026-11-14, user request).
#
# How the leading ERPs present a new user's access, and what this follows:
#   * Dynamics 365: roles bundle duties and privileges; before go-live the
#     administrator reviews the EFFECTIVE permissions a role gives.
#   * NetSuite: each permission is a level on one ladder - None, View, Create,
#     Edit, Full - and print comes with View; export is its own permission.
#   * SAP S/4HANA: business roles grant; restrictions narrow (Write / Read).
#
# Here: the business roles grant access (Odoo groups, record rules - the one
# permission engine, spec M29 §4). On a joiner or mover event the requester
# sees, per module, the level the chosen roles allow, and may NARROW it:
# No access (deny), View only, View + Create, or View + Create + Edit, plus
# separate Approve / Print / Export / Email switches. Narrowing is stored as
# a fix.module.permission row and enforced by the P03 workspace server on
# every request (records, forms, saves, workflow actions, report packs,
# PDF/Excel/CSV downloads and e-mails). Nothing here can grant MORE than the
# roles do: for more access, add a role (SoD-checked).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

# NetSuite-style ladder: each level includes the ones before it
LEVELS = [
    ("none", "No access"),
    ("view", "View"),
    ("create", "Create"),
    ("edit", "Edit"),
]
BULK = [
    ("roles", "Everything the roles allow"),
    ("view", "View only, in every module"),
    ("none", "No access anywhere (then open modules one by one)"),
]
RANK = {"none": 0, "view": 1, "create": 2, "edit": 3}
SWITCHES = ("can_approve", "can_print", "can_export", "can_email")
NEEDS = {
    "view": "viewing records",
    "create": "creating records",
    "edit": "editing records",
    "approve": "approving or processing records",
    "print": "printing (PDF)",
    "export": "exporting (Excel / CSV)",
    "email": "e-mailing reports",
}


def level_label(level):
    return dict(LEVELS).get(level or "none", level)


class FixModulePermission(models.Model):
    """A user's narrowed access to one workspace module. No row: the roles
    decide. A row: the user may do only what it ticks (and never more than
    the roles allow, which the Odoo access rules still enforce)."""

    _name = "fix.module.permission"
    _description = "Module Permission (narrowed access)"
    _order = "user_id, module_code"
    _rec_name = "module_name"

    user_id = fields.Many2one(
        "res.users", required=True, index=True, ondelete="cascade", string="User"
    )
    module_code = fields.Char(required=True, index=True, string="Module")
    module_name = fields.Char(string="Module Name")
    area = fields.Char()
    level = fields.Selection(LEVELS, required=True, default="view", string="Access Level")
    can_approve = fields.Boolean(string="Approve / Process")
    can_print = fields.Boolean(string="Print (PDF)")
    can_export = fields.Boolean(string="Export (Excel / CSV)")
    can_email = fields.Boolean(string="E-mail")
    event_id = fields.Many2one("fix.jml.event", string="Set By Event", ondelete="set null")
    set_on = fields.Datetime(default=fields.Datetime.now, readonly=True)

    _user_module_unique = models.Constraint(
        "UNIQUE (user_id, module_code)", "A user has one permission row per module."
    )

    def _fix_allows(self, need):
        self.ensure_one()
        rank = RANK.get(self.level, 0)
        if need in ("view", "create", "edit"):
            return rank >= RANK[need]
        if rank < RANK["view"]:
            return False
        return bool(self["can_%s" % need])

    @api.model
    def _fix_refusal(self, user, module_code, need):
        """None when allowed, else the message the workspace shows."""
        if not module_code:
            return None
        row = self.sudo().search(
            [("user_id", "=", user.id), ("module_code", "=", module_code)], limit=1
        )
        if not row or row._fix_allows(need):
            return None
        return (
            "Your access to %s does not include %s (set to: %s). Ask an Access Approver "
            "to change it with a mover event."
            % (row.module_name or module_code, NEEDS.get(need, need), row._fix_summary())
        )

    def _fix_summary(self):
        self.ensure_one()
        parts = [level_label(self.level)]
        if self.level != "none":
            parts += [
                label
                for name, label in (
                    ("can_approve", "Approve"),
                    ("can_print", "Print"),
                    ("can_export", "Export"),
                    ("can_email", "E-mail"),
                )
                if self[name]
            ]
        return ", ".join(parts)


class FixJmlPermissionLine(models.Model):
    """One module on a joiner / mover event's permission checklist. The
    allowed_* columns are what the chosen roles give (computed by the
    workspace from the real access rules); the requester may narrow."""

    _name = "fix.jml.permission.line"
    _description = "JML Module Permission Line"
    _order = "area, module_code"

    event_id = fields.Many2one(
        "fix.jml.event", required=True, index=True, ondelete="cascade", string="Event"
    )
    module_code = fields.Char(required=True, readonly=True, string="Code")
    module_name = fields.Char(readonly=True, string="Module")
    area = fields.Char(readonly=True)
    allowed_level = fields.Selection(LEVELS, readonly=True, string="Roles Allow")
    allowed_label = fields.Char(readonly=True, string="Roles Allow")
    level = fields.Selection(LEVELS, required=True, default="view", string="Access Level")
    can_approve = fields.Boolean(string="Approve")
    can_print = fields.Boolean(string="Print")
    can_export = fields.Boolean(string="Export")
    can_email = fields.Boolean(string="E-mail")

    def _fix_cap_from_roles(self):
        """M29-D4: the cap as the roles REALLY allow it now, derived from the
        event's roles — not the stored `allowed_level` column, which a forged
        grid write could carry (readonly is a view attribute, not an ORM one).
        Falls back to the stored column when the deriving method is absent."""
        self.ensure_one()
        event = self.event_id
        derive = getattr(event, "_fix_role_allowance", None)
        if derive and getattr(event, "role_id", False):
            try:
                allowed = derive(event._fix_roles())
                cap = (allowed.get(self.module_code) or (None, None))[0]
                if cap:
                    return cap
            except Exception:  # derivation is display-grade; the column stands
                pass
        return self.allowed_level

    @api.constrains("level", "can_approve", "can_print", "can_export", "can_email")
    def _check_within_roles(self):
        for line in self:
            cap = line._fix_cap_from_roles()
            if RANK.get(line.level, 0) > RANK.get(cap or "none", 0):
                raise ValidationError(
                    "%s: the chosen roles allow %s, not %s. To give more, add a role."
                    % (
                        line.module_name or line.module_code,
                        level_label(cap),
                        level_label(line.level),
                    )
                )
            if line.can_approve and RANK.get(cap or "none", 0) < RANK["edit"]:
                raise ValidationError(
                    "%s: the chosen roles do not allow approving or processing records."
                    % (line.module_name or line.module_code)
                )

    def write(self, vals):
        if not self.env.su:
            for line in self.sudo():
                if line.event_id.state != "pending":
                    raise UserError(
                        "%s is %s: its permissions cannot change."
                        % (line.event_id.name, line.event_id.state)
                    )
        if vals.get("level") == "none":
            vals = dict(vals, **{name: False for name in SWITCHES})
        return super().write(vals)

    def _fix_narrowed(self):
        """True when this line gives less than the roles allow."""
        self.ensure_one()
        allowed = RANK.get(self.allowed_level or "none", 0)
        if RANK.get(self.level, 0) < allowed:
            return True
        if self.level == "none":
            return False
        if allowed >= RANK["edit"] and not self.can_approve:
            return True
        return allowed >= RANK["view"] and not (
            self.can_print and self.can_export and self.can_email
        )
