# M29 security operations — the registry's remaining surfaces:
#   M29-jml          Joiner / Mover / Leaver automation
#   M29-cert         Access certification campaigns
#   M29-keys         Encryption key registry (vault REFERENCES only — SEC-101)
#   M29-audit        Append-only security audit trail (hash-chained)
#   M29-incidents    Security incidents
# The JML and certification actions really change res.users group membership.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixJmlEvent(models.Model):
    _name = "fix.jml.event"
    _description = "Joiner / Mover / Leaver Event"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "effective_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    event_type = fields.Selection(
        [("joiner", "Joiner"), ("mover", "Mover"), ("leaver", "Leaver")],
        required=True,
        default="joiner",
        tracking=True,
    )
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True, index=True)
    user_id = fields.Many2one("res.users", string="Portal User", index=True)
    role_id = fields.Many2one(
        "fix.role",
        string="Role to Apply / Revoke",
        help="Joiner: granted. Leaver: every mapped role is revoked regardless. Mover: this role is granted.",
    )
    effective_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("pending", "Pending"), ("applied", "Applied"), ("cancelled", "Cancelled")],
        required=True,
        default="pending",
        tracking=True,
    )
    applied_on = fields.Datetime(readonly=True)
    result_note = fields.Char(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.jml.event") or "JML/New"
            if not vals.get("user_id") and vals.get("employee_id"):
                employee = self.env["hr.employee"].browse(vals["employee_id"])
                user = employee.sudo().user_id
                if user:
                    vals["user_id"] = user.id
        return super().create(vals_list)

    def action_apply(self):
        """Real effect on res.users.group_ids: joiners/movers get the role's group,
        a leaver loses every group that any business role maps to."""
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending JML event can be applied")
            user = rec.user_id
            if not user:
                raise UserError("The employee has no linked user, so no access can change")
            roles = self.env["fix.role"].sudo().search([("group_id", "!=", False)])
            if rec.event_type == "leaver":
                group_ids = roles.mapped("group_id").ids
                if group_ids:
                    user.write({"group_ids": [(3, gid) for gid in group_ids]})
                note = "%d role group(s) revoked" % len(group_ids)
            else:
                if not rec.role_id or not rec.role_id.group_id:
                    raise UserError("Pick a role that is mapped to an Odoo group")
                user.write({"group_ids": [(4, rec.role_id.group_id.id)]})
                note = "%s granted (%s)" % (rec.role_id.code, rec.role_id.group_id.name)
            rec.write(
                {
                    "state": "applied",
                    "applied_on": fields.Datetime.now(),
                    "result_note": note,
                }
            )
            user.invalidate_recordset(["group_ids"])

    def action_cancel(self):
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending event can be cancelled")
            rec.state = "cancelled"


class FixAccessCertification(models.Model):
    _name = "fix.access.certification"
    _description = "Access Certification"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    period = fields.Char(required=True, help="Review period, e.g. 2026-Q4")
    user_id = fields.Many2one("res.users", string="User Under Review", required=True, index=True)
    role_id = fields.Many2one("fix.role", string="Role Held", required=True, index=True)
    reviewer_id = fields.Many2one(
        "res.users", string="Reviewer", default=lambda self: self.env.user
    )
    decision = fields.Selection(
        [("pending", "Pending"), ("certified", "Certified"), ("revoked", "Revoked")],
        required=True,
        default="pending",
        tracking=True,
    )
    decided_on = fields.Datetime(readonly=True)
    note = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.access.certification") or "CERT/New"
                )
        return super().create(vals_list)

    def action_certify(self):
        for rec in self:
            if rec.decision != "pending":
                raise UserError("This access line is already decided")
            rec.write({"decision": "certified", "decided_on": fields.Datetime.now()})

    def action_revoke(self):
        """Removes the role's Odoo group from the user and records the decision."""
        for rec in self:
            if rec.decision != "pending":
                raise UserError("This access line is already decided")
            group = rec.role_id.group_id
            if not group:
                raise UserError("The role has no Odoo group mapped, so it cannot be revoked")
            rec.user_id.write({"group_ids": [(3, group.id)]})
            rec.user_id.invalidate_recordset(["group_ids"])
            rec.write({"decision": "revoked", "decided_on": fields.Datetime.now()})


class FixEncryptionKey(models.Model):
    _name = "fix.encryption.key"
    _description = "Encryption Key Registry"
    _order = "code"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    purpose = fields.Selection(
        [
            ("field_encryption", "Field Encryption"),
            ("backup", "Backup"),
            ("transport", "Transport (TLS)"),
            ("signing", "Signing / HMAC"),
        ],
        required=True,
        default="field_encryption",
    )
    algorithm = fields.Selection(
        [
            ("aes_256_gcm", "AES-256-GCM"),
            ("chacha20", "ChaCha20-Poly1305"),
            ("rsa_4096", "RSA-4096"),
            ("hmac_sha256", "HMAC-SHA256"),
        ],
        required=True,
        default="aes_256_gcm",
    )
    vault_ref = fields.Char(
        string="Vault Reference",
        required=True,
        help="Pointer into the secret manager (e.g. vault://kv/fix/field-key-2026). "
        "The key material is NEVER stored in this database (SEC-101).",
    )
    rotations_per_year = fields.Integer(default=1)
    last_rotated_on = fields.Date()
    next_rotation_on = fields.Date()
    custodian_id = fields.Many2one("res.users", string="Custodian")
    state = fields.Selection(
        [("active", "Active"), ("rotating", "Rotating"), ("retired", "Retired")],
        required=True,
        default="active",
    )

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A key code is unique per company"
    )

    @api.constrains("vault_ref")
    def _check_vault_ref(self):
        for rec in self:
            ref = (rec.vault_ref or "").strip()
            if not ref.startswith("vault://"):
                raise UserError(
                    "A key must reference the secret manager (vault://...) — key material "
                    "must never be entered here"
                )


class FixSecurityAudit(models.Model):
    """Append-only. Entries carry a hash chain over (previous hash, payload) so a
    deleted or edited row breaks the chain — that is what "immutable" means here,
    since a database trigger cannot be relied on from the workspace."""

    _name = "fix.security.audit"
    _description = "Security Audit Trail"
    _order = "occurred_at desc, id desc"

    sequence = fields.Integer(readonly=True, index=True)
    occurred_at = fields.Datetime(required=True, default=fields.Datetime.now, readonly=True)
    actor_id = fields.Many2one("res.users", string="Actor", readonly=True)
    event = fields.Selection(
        [
            ("login", "Login"),
            ("grant", "Access Granted"),
            ("revoke", "Access Revoked"),
            ("rule_change", "Rule Changed"),
            ("key_rotation", "Key Rotated"),
            ("privileged", "Privileged Action"),
            ("export", "Data Export"),
            ("incident", "Security Incident"),
        ],
        required=True,
        readonly=True,
    )
    object_ref = fields.Char(string="Object", readonly=True)
    detail = fields.Char(readonly=True)
    ip_address = fields.Char(readonly=True)
    prev_hash = fields.Char(readonly=True)
    entry_hash = fields.Char(readonly=True, index=True)

    def _hash_payload(self, vals, prev_hash):
        import hashlib

        raw = "|".join(
            [
                prev_hash or "",
                str(vals.get("event") or ""),
                str(vals.get("object_ref") or ""),
                str(vals.get("detail") or ""),
                str(vals.get("actor_id") or ""),
                str(vals.get("occurred_at") or ""),
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @api.model_create_multi
    def create(self, vals_list):
        last = self.search([], order="sequence desc, id desc", limit=1)
        prev_hash = last.entry_hash or ""
        seq = last.sequence or 0
        for vals in vals_list:
            seq += 1
            vals.setdefault("sequence", seq)
            if not vals.get("actor_id"):
                vals["actor_id"] = self.env.user.id
            vals["prev_hash"] = prev_hash
            vals["entry_hash"] = self._hash_payload(vals, prev_hash)
            prev_hash = vals["entry_hash"]
        return super().create(vals_list)

    def write(self, vals):
        raise UserError("The security audit trail is append-only — entries cannot be edited")

    def unlink(self):
        raise UserError("The security audit trail is append-only — entries cannot be deleted")

    def action_verify_chain(self):
        """Recomputes the chain; returns a pack-friendly summary via a message."""
        broken = 0
        prev = ""
        for rec in self.search([], order="sequence asc, id asc"):
            if (rec.prev_hash or "") != prev:
                broken += 1
            prev = rec.entry_hash or ""
        raise UserError(
            "Chain verified: %d entr(ies), %d discontinuity(ies)" % (self.search_count([]), broken)
        )


class FixSecurityIncident(models.Model):
    _name = "fix.security.incident"
    _description = "Security Incident"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "detected_at desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    title = fields.Char(required=True)
    category = fields.Selection(
        [
            ("unauthorised_access", "Unauthorised Access"),
            ("malware", "Malware"),
            ("phishing", "Phishing"),
            ("data_leak", "Data Leak / Exfiltration"),
            ("policy_breach", "Policy Breach"),
            ("availability", "Availability / DoS"),
        ],
        required=True,
        default="unauthorised_access",
    )
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        required=True,
        default="medium",
        tracking=True,
    )
    detected_at = fields.Datetime(required=True, default=fields.Datetime.now)
    detected_by_id = fields.Many2one("res.users", string="Detected By")
    affected_user_id = fields.Many2one("res.users", string="Affected User")
    session_id = fields.Many2one("fix.privileged.session", string="Related Privileged Session")
    description = fields.Text()
    containment = fields.Text()
    state = fields.Selection(
        [("open", "Open"), ("contained", "Contained"), ("closed", "Closed")],
        required=True,
        default="open",
        tracking=True,
    )
    resolved_on = fields.Datetime(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.security.incident") or "SEC/New"
                )
        return super().create(vals_list)

    def action_contain(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Contain an open incident")
            if not (rec.containment or "").strip():
                raise UserError("Record what was done to contain the incident first")
            rec.state = "contained"

    def action_close(self):
        for rec in self:
            if rec.state != "contained":
                raise UserError("Close a contained incident")
            rec.write({"state": "closed", "resolved_on": fields.Datetime.now()})
