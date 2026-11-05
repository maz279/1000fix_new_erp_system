# M29 Identity, Access & Security — the operational records behind the access
# review: access requests with a real grant/revoke effect, SoD test runs,
# privileged sessions and the sensitive-field classification. Role definitions,
# record rules and the Odoo groups themselves are core/rbac models.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class FixAccessRequest(models.Model):
    _name = "fix.access.request"
    _description = "Access Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "requested_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    request_type = fields.Selection(
        [("grant", "Grant Role"), ("revoke", "Revoke Role"), ("elevate", "Temporary Elevation")],
        required=True,
        default="grant",
    )
    user_id = fields.Many2one("res.users", string="User", required=True, index=True)
    role_id = fields.Many2one("fix.role", string="Role", required=True, index=True)
    reason = fields.Text(required=True)
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user
    )
    requested_on = fields.Date(required=True, default=fields.Date.context_today)
    valid_until = fields.Date(help="Required for a temporary elevation")
    approver_id = fields.Many2one("res.users", string="Approver")
    decided_on = fields.Datetime()
    decision_note = fields.Char()
    state = fields.Selection(
        [
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("granted", "Granted"),
            ("revoked", "Revoked"),
        ],
        required=True,
        default="submitted",
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.access.request") or "AR/New"
                )
        return super().create(vals_list)

    @api.constrains("request_type", "valid_until")
    def _check_elevation_window(self):
        for rec in self:
            if rec.request_type == "elevate" and not rec.valid_until:
                raise ValidationError("A temporary elevation must state its valid-until date")

    def action_approve(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Approve a submitted request")
            rec.write(
                {
                    "state": "approved",
                    "approver_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )

    def action_reject(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Reject a submitted request")
            rec.write(
                {
                    "state": "rejected",
                    "approver_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )

    def action_grant(self):
        """Real effect: the role's Odoo group is added to (or removed from)
        the user — checked against the SoD register first (A10 P1-3,
        M60-5). A conflicting combination is refused unless the request
        itself is a valid waiver: an approver who is not the beneficiary,
        an expiry and a reason; a block control is refused outright."""
        Sod = self.env["fix.sod.control"]
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved request can be granted")
            group = rec.role_id.group_id
            if not group:
                raise UserError(
                    "Role %s has no Odoo group mapped, so it cannot be granted" % rec.role_id.code
                )
            if rec.request_type == "revoke":
                rec.user_id.write({"group_ids": [(3, group.id)]})
                rec.state = "revoked"
                continue
            waived = Sod.check_role_set(
                Sod._user_role_ids(rec.user_id) | {rec.role_id.id},
                waiver={
                    "approver_id": rec.approver_id.id,
                    "user_id": rec.user_id.id,
                    "valid_until": rec.valid_until,
                    "reason": rec.decision_note or rec.reason,
                },
            )
            rec.user_id.write({"group_ids": [(4, group.id)]})
            rec.state = "granted"
            for control in waived:
                rec.message_post(
                    body="SoD waiver applied — control %s (%s) accepted by %s, "
                    "expires %s."
                    % (control.code, control.name, rec.approver_id.name, rec.valid_until)
                )

    @api.model
    def cron_revoke_expired(self):
        """Daily (A10 P1-3): a waiver or elevation is only as real as its
        expiry. A granted request past its valid_until loses the group and
        is revoked — the chatter is the log."""
        today = fields.Date.today()
        stale = self.search(
            [
                ("state", "=", "granted"),
                ("valid_until", "!=", False),
                ("valid_until", "<", today),
            ]
        )
        for rec in stale:
            group = rec.role_id.group_id
            if group:
                rec.user_id.sudo().write({"group_ids": [(3, group.id)]})
            rec.write({"state": "revoked"})
            rec.message_post(
                body="Expired on %s — the access and its SoD waiver ended with "
                "it (role %s)." % (rec.valid_until, rec.role_id.code)
            )
        return len(stale)


class FixSodTest(models.Model):
    _name = "fix.sod.test"
    _description = "SoD Test Run"
    _order = "tested_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    control_id = fields.Many2one(
        "fix.sod.control", string="SoD Control", required=True, ondelete="cascade", index=True
    )
    tested_on = fields.Date(required=True, default=fields.Date.context_today)
    tested_by_id = fields.Many2one(
        "res.users", string="Tested By", default=lambda self: self.env.user
    )
    users_checked = fields.Integer()
    violations_found = fields.Integer(readonly=True)
    users_in_conflict = fields.Char(string="Conflicting Users", readonly=True)
    result = fields.Selection([("pass", "Pass"), ("fail", "Fail")], readonly=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.sod.test") or "SODT/New"
        return super().create(vals_list)

    def action_run(self):
        """Measures the conflict for real: users holding BOTH roles' groups."""
        for rec in self:
            control = rec.control_id
            group_a, group_b = control.role_a_id.group_id, control.role_b_id.group_id
            if not (group_a and group_b):
                raise UserError(
                    "Both roles on %s need an Odoo group before the test can run" % control.code
                )
            offenders = (
                self.env["res.users"]
                .sudo()
                .search(
                    [
                        ("group_ids", "in", group_a.id),
                        ("group_ids", "in", group_b.id),
                        ("active", "=", True),
                    ]
                )
            )
            rec.write(
                {
                    "users_checked": self.env["res.users"]
                    .sudo()
                    .search_count([("active", "=", True)]),
                    "violations_found": len(offenders),
                    "users_in_conflict": ", ".join(offenders.mapped("login"))[:250] or "—",
                    "result": "fail" if offenders else "pass",
                }
            )


class FixPrivilegedSession(models.Model):
    _name = "fix.privileged.session"
    _description = "Privileged Session"
    _order = "started_at desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    user_id = fields.Many2one("res.users", string="User", required=True, index=True)
    access_kind = fields.Selection(
        [
            ("sudo_admin", "Sudo / Admin"),
            ("db_console", "Database Console"),
            ("key_rotation", "Key Rotation"),
            ("data_export", "Bulk Data Export"),
        ],
        required=True,
        default="sudo_admin",
    )
    reason = fields.Char(required=True)
    ticket_ref = fields.Char(string="Ticket / Change Ref")
    started_at = fields.Datetime(required=True, default=fields.Datetime.now)
    ended_at = fields.Datetime()
    duration_minutes = fields.Integer(readonly=True)
    actions_count = fields.Integer()
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")], required=True, default="open"
    )

    def action_close(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Close an open session")
            now = fields.Datetime.now()
            minutes = 0
            if rec.started_at:
                minutes = int((now - rec.started_at).total_seconds() // 60)
            rec.write({"state": "closed", "ended_at": now, "duration_minutes": minutes})


class FixSensitiveField(models.Model):
    _name = "fix.sensitive.field"
    _description = "Sensitive Field Classification"
    _order = "model_name, field_name"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    model_name = fields.Char(string="Model", required=True, index=True)
    field_name = fields.Char(string="Field", required=True)
    sensitivity = fields.Selection(
        [
            ("s0", "S0 - Public"),
            ("s1", "S1 - Internal"),
            ("s2", "S2 - Confidential"),
            ("s3", "S3 - Restricted"),
        ],
        required=True,
        default="s2",
        help="The data-sensitivity level the classification policy assigns (S0–S3).",
    )
    data_class = fields.Selection(
        [
            ("pii", "Personal Data (PII)"),
            ("financial", "Financial"),
            ("health", "Health"),
            ("credential", "Credential / Secret"),
            ("biometric", "Biometric"),
        ],
        required=True,
        default="pii",
    )
    masking_rule = fields.Selection(
        [
            ("none", "No masking"),
            ("last4", "Show last 4"),
            ("full", "Fully masked"),
            ("hash", "Hashed"),
        ],
        required=True,
        default="last4",
    )
    lawful_basis = fields.Char(help="The PDPA lawful basis for processing this field")
    retention_note = fields.Char()
    active = fields.Boolean(default=True)

    _field_unique = models.Constraint(
        "UNIQUE (model_name, field_name, company_id)",
        "A field is classified once per company",
    )
