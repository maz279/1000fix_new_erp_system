# M29 Identity, Access & Security — the operational records behind the access
# review: access requests with a real grant/revoke effect, SoD test runs,
# privileged sessions and the sensitive-field classification. Role definitions,
# record rules and the Odoo groups themselves are core/rbac models.
#
# A12 X1: the access request keeps an OPERATIONAL two-person approval (per the
# report it is deliberately NOT routed through M63): the approver must differ
# from requester and beneficiary, must hold the Access Approver group or be
# the requester's manager, and the grant re-checks the approval and runs the
# SoD gate BEFORE performing the group change as a service.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

ELEVATION_PARAM = "fix_rbac_ext.elevation_max_days"


class FixAccessRequest(models.Model):
    _name = "fix.access.request"
    _description = "Access Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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

    def _fix_guarded_fields(self) -> set:
        # S2/S4: the decision record is set only by the decision actions; a
        # typed approval is a forged approval.
        return super()._fix_guarded_fields() | {
            "state",
            "approver_id",
            "decided_on",
            "decision_note",
        }

    def _fix_form_locked_fields(self) -> set:
        # after approval the request is pinned: role, user and type are what
        # was approved (S4) — corrections go through a new request.
        locked = set(super()._fix_form_locked_fields())
        for rec in self:
            if rec.state in ("approved", "granted", "revoked"):
                locked |= {"role_id", "user_id", "request_type", "valid_until"}
        return locked

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

    # ------------------------------------------------------------------
    # X1: approver authority
    # ------------------------------------------------------------------

    @api.model
    def _requester_managers(self, requester):
        """The requester's people managers (hr.employee.parent_id -> user)."""
        employees = self.env["hr.employee"].sudo().search([("user_id", "=", requester.id)])
        managers = self.env["res.users"]
        for employee in employees:
            if employee.parent_id and employee.parent_id.user_id:
                managers |= employee.parent_id.user_id
        return managers

    def _approver_authority(self, rec):
        """True when env.user may DECIDE this request: a member of the
        shipped Access Approver group, or the requester's manager. The
        requester themself never has authority (a manager-less self-loop —
        an employee whose own manager resolves to them — is not authority)."""
        user = self.env.user
        if self.env.su:
            return True
        if user in (rec.requested_by_id, rec.user_id):
            return False
        if user.has_group("cd_rbac_ext.group_access_approver"):
            return True
        return user in self._requester_managers(rec.requested_by_id)

    def _assert_decider(self, rec):
        if not self._approver_authority(rec):
            raise UserError(
                "Only an Access Approver (cd_rbac_ext.group_access_approver) or the "
                "requester's manager — never the requester or the beneficiary — may "
                "decide an access request."
            )

    # ------------------------------------------------------------------
    # Decision actions
    # ------------------------------------------------------------------

    def action_approve(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Approve a submitted request")
            self._assert_decider(rec)
            rec._guarded().write(
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
            self._assert_decider(rec)
            rec._guarded().write(
                {
                    "state": "rejected",
                    "approver_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )

    # ------------------------------------------------------------------
    # The grant (provisioning) — re-checks, SoD gate, then a sudo service
    # ------------------------------------------------------------------

    def _approval_is_intact(self, rec):
        """S4: the grant re-checks the decision, not just the state."""
        if rec.state != "approved":
            return False
        if not rec.approver_id or not rec.decided_on:
            return False
        return rec.approver_id not in (rec.requested_by_id, rec.user_id)

    def action_grant(self):
        """Real effect: the role's Odoo groups are added to (or removed from)
        the user. Re-checks the approval, runs the SoD gate, then performs
        the group change as a service — so the approver needs no Access
        Rights of their own (X1)."""
        Jml = self.env["fix.jml.event"]
        for rec in self:
            if not self._approval_is_intact(rec):
                raise UserError(
                    "Only an intact approved request can be granted: it must carry an "
                    "approver who is neither the requester nor the beneficiary"
                )
            role = rec.role_id
            groups = self.env["fix.sod.control"]._role_groups(role)
            if not groups:
                raise UserError(
                    "Role %s has no Odoo group mapped, so it cannot be granted" % role.code
                )
            if rec.request_type == "revoke":
                if not (set(rec.user_id.sudo().group_ids.ids) & set(groups.ids)):
                    raise UserError(
                        "%s does not currently hold any group mapped to %s, so there is "
                        "nothing to revoke" % (rec.user_id.login, role.code)
                    )
                removed = Jml._apply_role_revoke(rec.user_id, role)
                rec._guarded().write({"state": "revoked"})
                self.env["fix.security.audit"].log_event(
                    "revoke",
                    "fix.access.request,%d" % rec.id,
                    "role %s revoked from %s by %s on request %s (%d group(s) removed)"
                    % (role.code, rec.user_id.login, self.env.user.name, rec.name, len(removed)),
                )
                continue
            # grant / elevate: an expired elevation is never granted
            if rec.request_type == "elevate" and rec.valid_until < fields.Date.today():
                raise UserError(
                    "This elevation expired on %s — file a new request" % rec.valid_until
                )
            # R2: every held role x the incoming role, before anything changes
            self.env["fix.sod.control"].check_user_assignment(rec.user_id, role)
            granted = Jml._apply_role_grant(rec.user_id, role)
            rec._guarded().write({"state": "granted"})
            self.env["fix.security.audit"].log_event(
                "grant",
                "fix.access.request,%d" % rec.id,
                "role %s granted to %s by %s on request %s (%s)"
                % (
                    role.code,
                    rec.user_id.login,
                    self.env.user.name,
                    rec.name,
                    ", ".join(granted.mapped("name"))[:160],
                ),
            )

    # ------------------------------------------------------------------
    # R3: elevation expiry cron (a granted elevation past valid_until is
    # revoked automatically — the time-box is real)
    # ------------------------------------------------------------------

    @api.model
    def cron_expire_elevations(self):
        today = fields.Date.today()
        expired = self.search(
            [
                ("request_type", "=", "elevate"),
                ("state", "=", "granted"),
                ("valid_until", "<", today),
            ]
        )
        Jml = self.env["fix.jml.event"]
        for rec in expired:
            if self.env["fix.sod.control"]._role_groups(rec.role_id):
                removed = Jml._apply_role_revoke(rec.user_id, rec.role_id)
            else:
                removed = self.env["res.groups"]  # unmapped role: no access to remove
            rec._guarded().write({"state": "revoked"})
            self.env["fix.security.audit"].log_event(
                "elevation_expiry",
                "fix.access.request,%d" % rec.id,
                "elevation of %s expired %s: role %s revoked (%d group(s) removed)"
                % (rec.user_id.login, rec.valid_until, rec.role_id.code, len(removed)),
            )
        return len(expired)


class FixSodTest(models.Model):
    _name = "fix.sod.test"
    _description = "SoD Test Run"
    _inherit = ["fix.guarded.mixin"]
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

    def _fix_guarded_fields(self) -> set:
        # the measurement is computed by action_run, never typed (M29-3)
        return super()._fix_guarded_fields() | {"result", "violations_found", "users_in_conflict"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.sod.test") or "SODT/New"
        return super().create(vals_list)

    def action_run(self):
        """Measures the conflict for real through role resolution: users who
        hold at least one mapped group of EACH role (R1 makes the pairs
        distinguishable again). Internal users only — portal users are out
        of scope of the access register."""
        for rec in self:
            control = rec.control_id
            role_a, role_b = control.role_a_id, control.role_b_id
            groups_a = set(self.env["fix.sod.control"]._role_groups(role_a).ids)
            groups_b = set(self.env["fix.sod.control"]._role_groups(role_b).ids)
            if not (groups_a and groups_b):
                raise UserError(
                    "Both roles on %s need an Odoo group before the test can run" % control.code
                )
            candidates = (
                self.env["res.users"].sudo().search([("share", "=", False), ("active", "=", True)])
            )
            offenders = candidates.filtered(
                lambda u, a=groups_a, b=groups_b: (a & set(u.group_ids.ids))
                and (b & set(u.group_ids.ids))
            )
            rec._guarded().write(
                {
                    "users_checked": len(candidates),
                    "violations_found": len(offenders),
                    "users_in_conflict": ", ".join(offenders.mapped("login"))[:250] or "—",
                    "result": "fail" if offenders else "pass",
                }
            )


class FixPrivilegedSession(models.Model):
    _name = "fix.privileged.session"
    _description = "Privileged Session"
    _inherit = ["fix.guarded.mixin"]
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

    def _fix_guarded_fields(self) -> set:
        # the closure stamps the end and the duration is MEASURED (M29-3)
        return super()._fix_guarded_fields() | {"state", "ended_at", "duration_minutes"}

    def _fix_form_locked_fields(self) -> set:
        return super()._fix_form_locked_fields() | {"user_id", "started_at"}

    @api.model_create_multi
    def create(self, vals_list):
        # a session is opened in one's own name only (E60: a plain user
        # opened a db_console session in the admin's name)
        if not self.env.su:
            for vals in vals_list:
                vals.pop("user_id", None)
                vals["user_id"] = self.env.uid
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.privileged.session") or "PS/New"
                )
        return super().create(vals_list)

    def action_close(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Close an open session")
            if not self.env.su and self.env.user != rec.user_id:
                raise UserError("Only the session's own user (%s) may close it" % rec.user_id.login)
            now = fields.Datetime.now().replace(microsecond=0)
            minutes = 0
            if rec.started_at:
                minutes = int((now - rec.started_at).total_seconds() // 60)
            rec._guarded().write({"state": "closed", "ended_at": now, "duration_minutes": minutes})
            self.env["fix.security.audit"].log_event(
                "privileged",
                "fix.privileged.session,%d" % rec.id,
                "privileged session %s (%s) closed after %d minute(s) by %s"
                % (rec.name, rec.access_kind, minutes, self.env.user.name),
            )

    @api.model
    def cron_close_stale_sessions(self):
        """R3: a privileged session may not stay open forever. Open sessions
        older than the configured timeout are force-closed by the cron and
        the closure is written to the audit trail (loud, not silent)."""
        limit = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("fix_rbac_ext.privileged_session_timeout_minutes", 240)
        )
        cutoff = fields.Datetime.now().replace(microsecond=0) - timedelta(minutes=limit)
        stale = self.search([("state", "=", "open"), ("started_at", "<", cutoff)])
        for rec in stale:
            now = fields.Datetime.now().replace(microsecond=0)
            minutes = int((now - rec.started_at).total_seconds() // 60)
            rec._guarded().write({"state": "closed", "ended_at": now, "duration_minutes": minutes})
            self.env["fix.security.audit"].log_event(
                "session_timeout",
                "fix.privileged.session,%d" % rec.id,
                "privileged session %s (%s, user %s) FORCE-CLOSED by timeout after %d "
                "minute(s) (limit %d)"
                % (rec.name, rec.access_kind, rec.user_id.login, minutes, limit),
            )
        return len(stale)


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
