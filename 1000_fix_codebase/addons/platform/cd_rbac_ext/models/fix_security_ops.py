# M29 security operations — the registry's remaining surfaces:
#   M29-jml          Joiner / Mover / Leaver automation (+ the employee.left
#                    consumer, A12 X2: create AND apply the JML event,
#                    deactivate res.users, remove ALL groups, unassign ITSM
#                    assets, write the audit trail)
#   M29-cert         Access certification campaigns (FR-SEC-026 close-out)
#   M29-keys         Encryption key registry (vault REFERENCES only — SEC-101)
#   M29-audit        Append-only security audit trail (hash-chained, server
#                    written only — A12 R5)
#   M29-incidents    Security incidents (§8.3 closure discipline)
# The JML and certification actions really change res.users group membership.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

GRACE_PARAM = "fix_rbac_ext.certification_grace_days"
SESSION_TIMEOUT_PARAM = "fix_rbac_ext.privileged_session_timeout_minutes"


class FixJmlEvent(models.Model):
    _name = "fix.jml.event"
    _description = "Joiner / Mover / Leaver Event"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "applied_on", "result_note"}

    def _fix_form_locked_fields(self) -> set:
        return super()._fix_form_locked_fields() | {"user_id"}

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

    # ------------------------------------------------------------------
    # Provisioning services (run as sudo AFTER the checks — X1 pattern)
    # ------------------------------------------------------------------

    @api.model
    def _apply_role_grant(self, user, role):
        """Grant every Odoo group the role maps to. Runs the SoD gate first
        (A12 R2: all held roles x the new role)."""
        Sod = self.env["fix.sod.control"]
        Sod.check_user_assignment(user, role)
        groups = Sod._role_groups(role)
        if not groups:
            raise UserError("Role %s maps to no Odoo group, so it cannot be granted" % role.code)
        # A08 S4: the group write below runs as a service (sudo), and the
        # res.users SoD door lets superuser writes through as "data loading".
        # So this workflow grant checks the GROUP-pair duties itself, strict,
        # before anything changes. Role pairs stay with the A12/A10 gates
        # above: a request's approval is the waiver for a warn role control,
        # which a group-pair exception record is not.
        index = Sod._fix_index()
        before = Sod._fix_conflicts(user=user, index=index)
        after = Sod._fix_conflicts(user=user, extra_groups=groups, index=index)
        Sod._fix_enforce(
            user,
            before,
            before | (after - before).filtered(lambda c: c.control_type == "group"),
            "role %s granted" % role.code,
            strict=True,
        )
        user.sudo().write({"group_ids": [(4, gid) for gid in groups.ids]})
        user.invalidate_recordset(["group_ids"])
        return groups

    @api.model
    def _apply_role_revoke(self, user, role):
        """Remove the role's groups, EXCEPT groups another role the user
        still holds also requires (A12 R1: the coarse-revoke bug)."""
        groups = self.env["fix.sod.control"]._role_groups(role)
        if not groups:
            raise UserError("Role %s maps to no Odoo group, so it cannot be revoked" % role.code)
        held = self.env["fix.sod.control"].user_held_roles(user)
        others = (held - role).filtered(lambda r: r != role)
        still_required = self.env["res.groups"]
        for other in others:
            still_required |= self.env["fix.sod.control"]._role_groups(other)
        removable = groups - still_required
        if removable:
            user.sudo().write({"group_ids": [(3, gid) for gid in removable.ids]})
            user.invalidate_recordset(["group_ids"])
        return removable

    @api.model
    def _deprovision_user(self, user, source):
        """X2 / BRU-SEC-06: a leaver loses EVERYTHING — all groups (not only
        role-mapped ones) and the login itself. Records the audit row."""
        groups_before = user.sudo().group_ids
        user.sudo().write({"group_ids": [(5, 0, 0)], "active": False})
        user.invalidate_recordset(["group_ids"])
        self.env["fix.security.audit"].log_event(
            "leaver",
            "res.users,%d" % user.id,
            "leaver deprovisioned (%s): %d group(s) removed (%s), login deactivated"
            % (
                source,
                len(groups_before),
                ", ".join(groups_before.mapped("name"))[:160] or "none",
            ),
        )
        return len(groups_before)

    @api.model
    def _unassign_itsm_assets(self, employee):
        """P2 hand-off M66 -> M21 leaver: the leaver's ITSM assets go back to
        stock unassigned. Only the assignment is cleared; assets are never
        created or unlinked from here."""
        if "fix.itsm.asset" not in self.env:
            return 0
        assets = self.env["fix.itsm.asset"].sudo().search([("assigned_to_id", "=", employee.id)])
        if assets:
            assets.write({"assigned_to_id": False})
            self.env["fix.security.audit"].log_event(
                "itsm_asset_unassign",
                "hr.employee,%d" % employee.id,
                "%d ITSM asset(s) unassigned on leaver: %s"
                % (len(assets), ", ".join(assets.mapped("name"))[:180]),
            )
        return len(assets)

    # ------------------------------------------------------------------
    # The employee.left consumer (A12 X2, P2 hand-off M21 -> M29)
    # ------------------------------------------------------------------

    @api.model
    def consume_employee_left(self, event):
        """fix.event.consumer target for `employee.left` (cd_employee_core
        publishes it through the transactional outbox; the relay calls this
        as superuser). Idempotent: a second delivery for an already
        deprovisioned employee is a no-op."""
        payload = event.get("payload") or {}
        employee_id = payload.get("employee_id") or event.get("aggregate_id")
        employee = self.env["hr.employee"].sudo().browse(int(employee_id or 0)).exists()
        if not employee:
            return True
        already = self.sudo().search(
            [
                ("event_type", "=", "leaver"),
                ("employee_id", "=", employee.id),
                ("state", "=", "applied"),
            ],
            limit=1,
        )
        if already:
            return True
        jml = self.sudo().create(
            {
                "event_type": "leaver",
                "employee_id": employee.id,
                "effective_on": payload.get("left_date") or fields.Date.today(),
                "company_id": employee.company_id.id or self.env.company.id,
            }
        )
        if not jml.user_id:
            # no linked login: nothing to deprovision, but the assets still
            # go back to stock and the event is recorded — never dead-letter.
            assets = self._unassign_itsm_assets(employee)
            jml._guarded().write(
                {
                    "state": "applied",
                    "applied_on": fields.Datetime.now(),
                    "result_note": (
                        "leaver with no linked user: %d ITSM asset(s) unassigned" % assets
                    )[:250],
                }
            )
            return True
        jml.action_apply()
        return True

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _assert_apply_authority(self):
        """Provisioning changes real access: only an Access Approver, a
        Settings (Access Rights) administrator or the superuser may apply."""
        if self.env.su or self.env.user.has_group("base.group_erp_manager"):
            return
        if self.env.user.has_group("cd_rbac_ext.group_access_approver"):
            return
        raise UserError(
            "Only an Access Approver (cd_rbac_ext.group_access_approver) or an "
            "Access Rights administrator may apply a JML event."
        )

    def action_apply(self):
        """Real effect on res.users.group_ids: joiners/movers get the role's
        groups after the SoD gate; a leaver loses EVERY group and the login."""
        self._assert_apply_authority()
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending JML event can be applied")
            user = rec.user_id
            if not user:
                raise UserError("The employee has no linked user, so no access can change")
            if rec.event_type == "leaver":
                count = self._deprovision_user(user, "jml %s" % rec.name)
                assets = self._unassign_itsm_assets(rec.employee_id)
                note = (
                    "leaver applied: %d group(s) removed, login deactivated, %d ITSM asset(s) unassigned"
                    % (
                        count,
                        assets,
                    )
                )
            else:
                if not rec.role_id:
                    raise UserError("Pick a role for a %s event" % rec.event_type)
                groups = self._apply_role_grant(user, rec.role_id)
                note = "%s granted (%s)" % (rec.role_id.code, ", ".join(groups.mapped("name")))
            rec._guarded().write(
                {"state": "applied", "applied_on": fields.Datetime.now(), "result_note": note[:250]}
            )

    def action_cancel(self):
        self._assert_apply_authority()
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending event can be cancelled")
            rec._guarded().write({"state": "cancelled"})


class FixAccessCertification(models.Model):
    _name = "fix.access.certification"
    _description = "Access Certification"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    due_on = fields.Date(
        string="Due On",
        default=lambda self: fields.Date.today()
        + timedelta(days=int(self.env["ir.config_parameter"].sudo().get_param(GRACE_PARAM, 14))),
        help="FR-SEC-026: a line still pending after this date is revoked by the "
        "close-out cron. Grace days: ir.config_parameter %s." % GRACE_PARAM,
    )
    note = fields.Char()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"decision", "decided_on"}

    def _fix_form_locked_fields(self) -> set:
        return super()._fix_form_locked_fields() | {"user_id", "role_id", "reviewer_id"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.access.certification") or "CERT/New"
                )
        return super().create(vals_list)

    @api.constrains("user_id", "reviewer_id")
    def _check_reviewer_not_reviewed(self):
        for rec in self:
            if rec.reviewer_id and rec.reviewer_id == rec.user_id:
                raise ValidationError(
                    "The reviewer may not be the user under review (self-certification)."
                )

    def _assert_reviewer(self):
        """M29-7: only the ASSIGNED reviewer decides this line (or the
        superuser / close-out cron)."""
        for rec in self:
            if self.env.su or self.env.user == rec.reviewer_id:
                continue
            raise UserError(
                "This certification line is assigned to %s; only that reviewer decides it."
                % (rec.reviewer_id.name or "nobody")
            )

    def action_certify(self):
        """Certify = keep the access. The SoD gate runs here too (R2): a
        reviewer may not certify access that now conflicts with what the user
        holds — they must revoke instead."""
        self._assert_reviewer()
        for rec in self:
            if rec.decision != "pending":
                raise UserError("This access line is already decided")
            self.env["fix.sod.control"].check_user_assignment(rec.user_id, rec.role_id)
            rec._guarded().write({"decision": "certified", "decided_on": fields.Datetime.now()})
            self.env["fix.security.audit"].log_event(
                "certification",
                "fix.access.certification,%d" % rec.id,
                "access certified (kept): %s keeps %s for %s by %s"
                % (rec.user_id.login, rec.role_id.code, rec.period, self.env.user.name),
            )

    def action_revoke(self):
        """Removes the role's groups from the user. The business check runs
        as the reviewer; the group change runs as a service, so a
        manager-reviewer without Access Rights can still revoke (M29-7/E52)."""
        self._assert_reviewer()
        for rec in self:
            if rec.decision != "pending":
                raise UserError("This access line is already decided")
            removed = self.env["fix.jml.event"]._apply_role_revoke(rec.user_id, rec.role_id)
            rec._guarded().write({"decision": "revoked", "decided_on": fields.Datetime.now()})
            self.env["fix.security.audit"].log_event(
                "certification",
                "fix.access.certification,%d" % rec.id,
                "access revoked on review: %s loses %s group(s) for %s by %s"
                % (rec.user_id.login, len(removed), rec.period, self.env.user.name),
            )

    @api.model
    def cron_close_certifications(self):
        """R3 / FR-SEC-026: unconfirmed access is revoked automatically. Any
        line still pending past its due date is revoked by the close-out."""
        today = fields.Date.today()
        overdue = self.search([("decision", "=", "pending"), ("due_on", "<", today)])
        for rec in overdue:
            removed = 0
            mapped = self.env["fix.sod.control"]._role_groups(rec.role_id)
            if rec.user_id.active and mapped:
                removed_groups = self.env["fix.jml.event"]._apply_role_revoke(
                    rec.user_id, rec.role_id
                )
                removed = len(removed_groups)
            rec._guarded().write(
                {
                    "decision": "revoked",
                    "decided_on": fields.Datetime.now(),
                    "note": (
                        "auto-revoked (FR-SEC-026): certification period lapsed %s; "
                        "%d group(s) removed" % (rec.due_on, removed)
                    )[:250],
                }
            )
            self.env["fix.security.audit"].log_event(
                "certification",
                "fix.access.certification,%d" % rec.id,
                "close-out: unconfirmed access %s / %s revoked for %s (due %s)"
                % (rec.user_id.login, rec.role_id.code, rec.period, rec.due_on),
            )
        return len(overdue)


class FixEncryptionKey(models.Model):
    _name = "fix.encryption.key"
    _description = "Encryption Key Registry"
    _inherit = ["fix.guarded.mixin"]
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
    successor_id = fields.Many2one(
        "fix.encryption.key", string="Rotated Into", readonly=True, copy=False
    )
    state = fields.Selection(
        [("active", "Active"), ("rotating", "Rotating"), ("retired", "Retired")],
        required=True,
        default="active",
    )

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A key code is unique per company"
    )

    def _fix_guarded_fields(self) -> set:
        # state and the rotation dates change only through action_rotate; the
        # vault reference and custodian are master data guarded by the
        # key-custodian ACL instead (they must remain settable at create).
        return super()._fix_guarded_fields() | {"state", "last_rotated_on", "next_rotation_on"}

    def _fix_form_locked_fields(self) -> set:
        return super()._fix_form_locked_fields() | {"vault_ref", "custodian_id", "successor_id"}

    @api.constrains("vault_ref")
    def _check_vault_ref(self):
        for rec in self:
            ref = (rec.vault_ref or "").strip()
            if not ref.startswith("vault://"):
                raise UserError(
                    "A key must reference the secret manager (vault://...) — key material "
                    "must never be entered here"
                )

    def _assert_custodian(self):
        """R5 / M29-8: only a Key Custodian (cd_rbac_ext.group_key_custodian,
        shipped EMPTY — an appointment the business makes) may rotate."""
        if self.env.su or self.env.user.has_group("cd_rbac_ext.group_key_custodian"):
            return
        raise UserError(
            "Only a Key Custodian (cd_rbac_ext.group_key_custodian) may rotate keys. "
            "The group ships empty; appointing one is a business decision."
        )

    def action_rotate(self, new_vault_ref=None):
        """REAL rotation (R5): registers the successor key version in the
        vault, retires the old one, sets the rotation clock and writes the
        `key_rotation` audit event. The material itself lives in the vault —
        this register never sees it (SEC-101)."""
        self._assert_custodian()
        Key = self.env["fix.encryption.key"]
        for rec in self:
            if rec.state != "active":
                raise UserError("Rotate an active key (%s is %s)" % (rec.code, rec.state))
            ref = (new_vault_ref or "").strip()
            if not ref.startswith("vault://"):
                raise UserError(
                    "The successor must reference the secret manager (vault://...) — the "
                    "new key is generated there, never typed here"
                )
            same_prefix = Key.search_count(
                [("code", "=like", rec.code + "/V%"), ("company_id", "=", rec.company_id.id)]
            )
            successor = Key.create(
                {
                    "code": "%s/V%d" % (rec.code, same_prefix + 1),
                    "name": "%s (rotated %s)" % (rec.name, fields.Date.today()),
                    "company_id": rec.company_id.id,
                    "purpose": rec.purpose,
                    "algorithm": rec.algorithm,
                    "vault_ref": ref,
                    "rotations_per_year": rec.rotations_per_year,
                    "custodian_id": rec.custodian_id.id or self.env.uid,
                    "state": "active",
                }
            )
            today = fields.Date.today()
            interval = 365 // max(rec.rotations_per_year, 1)
            rec._guarded().write(
                {
                    "state": "retired",
                    "last_rotated_on": today,
                    "next_rotation_on": today + timedelta(days=interval),
                    "successor_id": successor.id,
                }
            )
            self.env["fix.security.audit"].log_event(
                "key_rotation",
                "fix.encryption.key,%d" % rec.id,
                "key %s rotated into %s (%s -> %s) by %s"
                % (rec.code, successor.code, rec.vault_ref, ref, self.env.user.name),
            )


class FixSecurityAudit(models.Model):
    """Append-only, hash-chained, and SYSTEM-WRITTEN (A12 R5): the actor,
    the time, the sequence and both hashes are set by the server and refuse
    caller-supplied values. No user ACL carries create — code appends rows
    through log_event(). Entries carry a hash chain over (previous hash,
    payload) so a deleted or edited row breaks the chain — that is what
    "immutable" means here, since a database trigger cannot be relied on
    from the workspace."""

    _name = "fix.security.audit"
    _description = "Security Audit Trail"
    _order = "occurred_at desc, id desc"

    sequence = fields.Integer(readonly=True, index=True)
    occurred_at = fields.Datetime(required=True, default=fields.Datetime.now, readonly=True)
    actor_id = fields.Many2one("res.users", string="Actor", readonly=True)
    # Free-form on purpose: it is the cross-builder contract (B3 integration
    # events, B5 gateway events...) — a fixed selection would refuse them.
    event = fields.Char(required=True, index=True)
    object_ref = fields.Char(string="Object", readonly=True)
    detail = fields.Char(readonly=True)
    ip_address = fields.Char(readonly=True)
    prev_hash = fields.Char(readonly=True)
    entry_hash = fields.Char(readonly=True, index=True)

    # fields only the server may set; create() strips them from any caller
    _SYSTEM_SET = ("sequence", "occurred_at", "actor_id", "prev_hash", "entry_hash")

    def _hash_payload(self, vals, prev_hash):
        import hashlib

        def _plain(value):
            if hasattr(value, "strftime"):  # datetime: hash the stored precision
                return value.strftime("%Y-%m-%d %H:%M:%S")
            return str(value or "")

        raw = "|".join(
            [
                prev_hash or "",
                _plain(vals.get("event")),
                _plain(vals.get("object_ref")),
                _plain(vals.get("detail")),
                _plain(vals.get("actor_id")),
                _plain(vals.get("occurred_at")),
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @api.model
    def log_event(self, event, object_ref, detail=None):
        """B1 cross-builder contract (A12 brief): append one chain-hashed,
        server-stamped row. Call it as
            env["fix.security.audit"].log_event(
                "integration.key_rotated", "fix.api.consumer,42", "detail...")
        (a `.sudo().log_event(...)` call site also works, but then the actor
        column records the service user — call it on the caller's env and it
        records the calling user; log_event escalates to write itself).
        The time is the server clock, the sequence and both hashes are
        computed here. Returns the row."""
        actor = self.env.uid
        return (
            self.sudo()
            .with_context(fix_audit_actor=actor)
            .create(
                {
                    "event": (event or "")[:120],
                    "object_ref": (object_ref or "")[:250],
                    "detail": (detail or "")[:250],
                }
            )
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            for name in self._SYSTEM_SET:
                vals.pop(name, None)  # server-set; caller values are refused
            vals["occurred_at"] = fields.Datetime.now().replace(microsecond=0)
            # the actor is the writing environment's user; log_event carries
            # the calling user through the context. The key is honoured only
            # under su — no group carries create, so a non-superuser caller
            # never reaches this body (AccessError) to spoof it.
            actor = (
                int(self.env.context.get("fix_audit_actor") or 0)
                if (self.env.su and self.env.context.get("fix_audit_actor"))
                else 0
            )
            vals["actor_id"] = actor or self.env.uid
        last = self.search([], order="sequence desc, id desc", limit=1)
        prev_hash = last.entry_hash or ""
        seq = last.sequence or 0
        for vals in vals_list:
            seq += 1
            vals["sequence"] = seq
            vals["prev_hash"] = prev_hash
            vals["entry_hash"] = self._hash_payload(vals, prev_hash)
            prev_hash = vals["entry_hash"]
        return super().create(vals_list)

    def write(self, vals):
        raise UserError("The security audit trail is append-only — entries cannot be edited")

    def unlink(self):
        raise UserError("The security audit trail is append-only — entries cannot be deleted")

    def action_verify_chain(self):
        """Recomputes EVERY row's entry_hash from its stored payload and
        checks the prev_hash links (R5: the old verifier only compared
        links, so an in-row edit went undetected). Raises the summary."""
        rows = self.search([], order="sequence asc, id asc")
        broken = 0
        prev = ""
        for rec in rows:
            recomputed = self._hash_payload(
                {
                    "event": rec.event,
                    "object_ref": rec.object_ref,
                    "detail": rec.detail,
                    "actor_id": rec.actor_id.id or "",
                    "occurred_at": rec.occurred_at,
                },
                prev,
            )
            if (rec.prev_hash or "") != prev or (rec.entry_hash or "") != recomputed:
                broken += 1
            prev = rec.entry_hash or ""
        raise UserError("Chain verified: %d entr(ies), %d discontinuity(ies)" % (len(rows), broken))


class FixSecurityIncident(models.Model):
    _name = "fix.security.incident"
    _description = "Security Incident"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    root_cause = fields.Text(help="Required before closure: what allowed the incident (§8.3).")
    breach_assessment = fields.Text(
        help="Required before closure for data leaks: was personal data exposed, how many "
        "data subjects, does the Bangladesh PDPA 2026 notification clock apply?"
    )
    severity_set_by_id = fields.Many2one("res.users", string="Severity Set By", readonly=True)
    severity_confirmed_by_id = fields.Many2one(
        "res.users", string="Severity Confirmed By", readonly=True
    )
    state = fields.Selection(
        [("open", "Open"), ("contained", "Contained"), ("closed", "Closed")],
        required=True,
        default="open",
        tracking=True,
    )
    resolved_on = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        # severity changes only through the two-person action; state and
        # resolution time only through contain/close.
        return super()._fix_guarded_fields() | {"state", "severity", "resolved_on"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.security.incident") or "SEC/New"
                )
            vals["severity_set_by_id"] = self.env.uid
        return super().create(vals_list)

    def action_contain(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Contain an open incident")
            if len((rec.containment or "").strip()) < 20:
                raise UserError(
                    "Record what was done to contain the incident first (at least a "
                    "sentence — a marker like 'x' is not containment)"
                )
            rec._guarded().write({"state": "contained"})

    def action_close(self):
        """§8.3: close needs containment, a root cause and (for a data leak)
        a breach assessment; the resolution time is stamped here, never
        typed. Writes the audit row."""
        for rec in self:
            if rec.state != "contained":
                raise UserError("Close a contained incident")
            if len((rec.containment or "").strip()) < 20:
                raise UserError("The incident is not contained: record the containment first")
            if len((rec.root_cause or "").strip()) < 20:
                raise UserError("Record the root cause before closing (at least a sentence)")
            if rec.category == "data_leak" and len((rec.breach_assessment or "").strip()) < 20:
                raise UserError(
                    "A data-leak incident needs a breach assessment (personal data exposed? "
                    "PDPA notification clock?) before it can close"
                )
            resolved_on = fields.Datetime.now()
            rec._guarded().write({"state": "closed", "resolved_on": resolved_on})
            self.env["fix.security.audit"].log_event(
                "incident",
                "fix.security.incident,%d" % rec.id,
                "incident closed: %s (%s) resolved %s by %s"
                % (rec.title, rec.severity, resolved_on, self.env.user.name),
            )

    def action_set_severity(self, severity, confirmed_by_id=None):
        """R5: a severity change is a two-person control — the caller and a
        DIFFERENT internal user who confirms it. Both are recorded."""
        valid = {key for key, _lbl in type(self).severity.selection}
        if severity not in valid:
            raise UserError("Severity must be one of %s" % ", ".join(sorted(valid)))
        witness = self.env["res.users"].browse(int(confirmed_by_id or 0)).exists()
        if not witness or witness.id == self.env.uid:
            raise UserError(
                "Changing an incident's severity needs a second person: pass the "
                "confirming user (confirmed_by_id), different from yourself."
            )
        for rec in self:
            old = rec.severity
            rec._guarded().write(
                {
                    "severity": severity,
                    "severity_set_by_id": self.env.uid,
                    "severity_confirmed_by_id": witness.id,
                }
            )
            self.env["fix.security.audit"].log_event(
                "incident",
                "fix.security.incident,%d" % rec.id,
                "severity %s -> %s by %s confirmed by %s"
                % (old, severity, self.env.user.name, witness.name),
            )
