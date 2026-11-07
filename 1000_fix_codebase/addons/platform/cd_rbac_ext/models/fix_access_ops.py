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
from odoo.exceptions import AccessError, UserError, ValidationError

ELEVATION_PARAM = "fix_rbac_ext.elevation_max_days"
ELEVATION_DEFAULT_DAYS = 30
BREAK_GLASS_PARAM = "fix_rbac_ext.break_glass_max_hours"
BREAK_GLASS_DEFAULT_HOURS = 4.0
APPROVER_GROUP = "cd_rbac_ext.group_access_approver"


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

    # what the approver approved: changing any of these after submission would
    # turn an approval for one thing into a grant of another (E2)
    _PINNED = (
        "role_id",
        "user_id",
        "request_type",
        "valid_until",
        "reason",
        "requested_on",
        "company_id",
    )

    def _fix_guarded_fields(self) -> set:
        # S2/S4: the decision record is set only by the decision actions; a
        # typed approval is a forged approval. requested_by_id names who may
        # not decide, so it is never typed either.
        return super()._fix_guarded_fields() | {
            "state",
            "approver_id",
            "decided_on",
            "decision_note",
            "requested_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        # after approval the request is pinned: role, user and type are what
        # was approved (S4) — corrections go through a new request.
        locked = set(super()._fix_form_locked_fields())
        if any(rec.state != "submitted" for rec in self.sudo()):
            locked |= set(self._PINNED)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.access.request") or "AR/New"
                )
            if not self.env.su:
                vals["requested_by_id"] = self.env.uid
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            pinned = set(self._PINNED) & set(vals)
            for rec in self:
                changed = [n for n in pinned if rec._fix_guard_differs(n, vals[n], rec[n])]
                if not changed:
                    continue
                if rec.state != "submitted":
                    raise UserError(
                        "%s is %s: what was decided cannot change. File a new request."
                        % (rec.name, rec.state)
                    )
                if rec.requested_by_id != self.env.user:
                    raise UserError("Only the requester can edit access request %s." % rec.name)
        return super().write(vals)

    @api.model
    def _fix_elevation_max_days(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(ELEVATION_PARAM)
        try:
            value = int(raw) if raw else ELEVATION_DEFAULT_DAYS
        except (TypeError, ValueError):
            value = ELEVATION_DEFAULT_DAYS
        return max(1, value)

    @api.constrains("request_type", "valid_until")
    def _check_elevation_window(self):
        limit = fields.Date.context_today(self) + timedelta(days=self._fix_elevation_max_days())
        for rec in self:
            if rec.request_type != "elevate":
                continue
            if not rec.valid_until:
                raise ValidationError("A temporary elevation must state its valid-until date")
            if rec.valid_until > limit:
                raise ValidationError(
                    "A temporary elevation may run at most %d days (%s). Request a role grant "
                    "for standing access." % (self._fix_elevation_max_days(), ELEVATION_PARAM)
                )

    @api.constrains("user_id", "role_id", "request_type")
    def _check_no_duplicate_open_request(self):
        for rec in self:
            duplicate = self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("user_id", "=", rec.user_id.id),
                    ("role_id", "=", rec.role_id.id),
                    ("request_type", "=", rec.request_type),
                    ("state", "in", ("submitted", "approved")),
                ]
            )
            if duplicate:
                raise ValidationError(
                    "An identical request for %s / %s is already open."
                    % (rec.user_id.sudo().login, rec.role_id.code)
                )

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

    def _user_may_decide(self, user, rec):
        """A member of the shipped Access Approver group, or the requester's
        manager. The requester and the beneficiary never have authority (a
        manager-less self-loop — an employee whose own manager resolves to
        them — is not authority)."""
        user = user.sudo()
        if user in (rec.sudo().requested_by_id, rec.sudo().user_id) or not user.active:
            return False
        if user.has_group(APPROVER_GROUP):
            return True
        return user in self._requester_managers(rec.sudo().requested_by_id)

    def _approver_authority(self, rec):
        """True when env.user may DECIDE this request."""
        return self.env.su or self._user_may_decide(self.env.user, rec)

    def _assert_decider(self, rec):
        if not self._approver_authority(rec):
            raise UserError(
                "Only an Access Approver (cd_rbac_ext.group_access_approver) or the "
                "requester's manager — never the requester or the beneficiary — may "
                "decide an access request."
            )

    def _fix_audit_decision(self, event, rec, note=None):
        self.env["fix.security.audit"].log_event(
            event,
            "fix.access.request,%d" % rec.id,
            "%s of %s for %s on %s by %s%s"
            % (
                rec.request_type,
                rec.role_id.code,
                rec.user_id.sudo().login,
                rec.name,
                self.env.user.name,
                (": %s" % note) if note else "",
            ),
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
            self._fix_audit_decision("access_approved", rec)

    def action_reject(self, reason=None):
        """A rejection says why: the requester reads it, and an audit needs it."""
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why this request is rejected.")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Reject a submitted request")
            self._assert_decider(rec)
            rec._guarded().write(
                {
                    "state": "rejected",
                    "approver_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "decision_note": reason[:250],
                }
            )
            self._fix_audit_decision("access_rejected", rec, reason)

    # ------------------------------------------------------------------
    # The grant (provisioning) — re-checks, SoD gate, then a sudo service
    # ------------------------------------------------------------------

    def _approval_is_intact(self, rec):
        """S4: the grant re-checks the decision, not just the state, and that
        the approver still has the authority they decided with (E23)."""
        if rec.state != "approved":
            return False
        if not rec.approver_id or not rec.decided_on:
            return False
        if rec.approver_id in (rec.requested_by_id, rec.user_id):
            return False
        return rec.approver_id._is_superuser() or self._user_may_decide(rec.approver_id, rec)

    def _assert_may_execute(self, rec):
        """E23: executing the grant is a privileged act of its own: the approver,
        an Access Approver or an Access Rights administrator, and never the
        requester or the beneficiary."""
        user = self.env.user
        if self.env.su:
            return
        if user in (rec.requested_by_id, rec.user_id) or not (
            user == rec.approver_id
            or user.has_group(APPROVER_GROUP)
            or user.has_group("base.group_erp_manager")
        ):
            raise UserError(
                "Only the approver, an Access Approver or an Access Rights administrator "
                "(never the requester or the beneficiary) may execute an approved request."
            )

    def action_grant(self):
        """Real effect: the role's Odoo groups are added to (or removed from)
        the user. Re-checks the approval, runs the SoD gate (A10 P1-3: the
        approved request itself is the waiver for a warn control — an approver
        who is not the beneficiary, an expiry and a reason; a block control
        needs an approved SoD exception), then performs the group change as a
        service through the JML chain — so the approver needs no Access Rights
        of their own (X1)."""
        Jml = self.env["fix.jml.event"]
        Sod = self.env["fix.sod.control"]
        for rec in self:
            self._assert_may_execute(rec)
            if not self._approval_is_intact(rec):
                raise UserError(
                    "Only an intact approved request can be granted: it must carry an "
                    "approver who is neither the requester nor the beneficiary and who "
                    "still has the authority to decide it"
                )
            role = rec.role_id
            user = rec.user_id.sudo()
            groups = Sod._role_groups(role)
            if not groups:
                raise UserError(
                    "Role %s has no Odoo group mapped, so it cannot be granted" % role.code
                )
            if rec.request_type == "revoke":
                if not (set(user.group_ids.ids) & set(groups.ids)):
                    raise UserError(
                        "%s does not currently hold any group mapped to %s, so there is "
                        "nothing to revoke" % (user.login, role.code)
                    )
                removed = Jml._apply_role_revoke(user, role, "revoke request %s" % rec.name)
                rec._guarded().write({"state": "revoked"})
                self.env["fix.security.audit"].log_event(
                    "revoke",
                    "fix.access.request,%d" % rec.id,
                    "role %s revoked from %s by %s on request %s (%d group(s) removed)"
                    % (role.code, user.login, self.env.user.name, rec.name, len(removed)),
                )
                continue
            # grant / elevate: an expired elevation is never granted
            if rec.request_type == "elevate" and rec.valid_until < fields.Date.today():
                raise UserError(
                    "This elevation expired on %s — file a new request" % rec.valid_until
                )
            # R2 + A10 P1-3: every held role x the incoming role, before
            # anything changes; the approved request is the waiver record
            # (approver ≠ beneficiary, expiry, reason)
            waived = Sod.check_role_set(
                Sod._user_role_ids(user) | {role.id},
                waiver={
                    "approver_id": rec.approver_id.id,
                    "user_id": user.id,
                    "valid_until": rec.valid_until,
                    "reason": rec.decision_note or rec.reason,
                },
                user=user,
                incoming=role,
            )
            granted = Jml._apply_role_grant(
                user, role, source="fix.access.request,%d" % rec.id, request=rec
            )
            rec._guarded().write({"state": "granted"})
            self.env["fix.security.audit"].log_event(
                "grant",
                "fix.access.request,%d" % rec.id,
                "role %s granted to %s by %s on request %s (%s)"
                % (
                    role.code,
                    user.login,
                    self.env.user.name,
                    rec.name,
                    ", ".join(granted.mapped("name"))[:160],
                ),
            )
            for control in waived:
                rec.message_post(
                    body="SoD waiver applied — control %s (%s) accepted by %s, "
                    "expires %s."
                    % (control.code, control.name, rec.approver_id.name, rec.valid_until)
                )

    # ------------------------------------------------------------------
    # R3: the expiry clock. A granted request past valid_until is revoked:
    # the time-box is real, whether it is an elevation or a time-boxed grant.
    # ------------------------------------------------------------------

    @api.model
    def cron_expire_elevations(self):
        if not self.env.su:
            raise AccessError("The access expiry clock runs from its scheduled job only.")
        today = fields.Date.today()
        expired = self.search(
            [
                ("request_type", "in", ("grant", "elevate")),
                ("state", "=", "granted"),
                ("valid_until", "!=", False),
                ("valid_until", "<", today),
            ]
        )
        Jml = self.env["fix.jml.event"]
        Assignment = self.env["fix.role.assignment"]
        for rec in expired:
            role, user = rec.role_id, rec.user_id
            live = Assignment._fix_live(user, role)
            removed = self.env["res.groups"]
            # the role also stands on a later or permanent assignment: that one keeps it
            kept = bool(live) and live.request_id != rec
            if not kept and self.env["fix.sod.control"]._role_groups(role):
                # unmapped role: no access to remove
                removed = Jml._apply_role_revoke(
                    user, role, "%s expired %s" % (rec.name, rec.valid_until)
                )
            rec._guarded().write({"state": "revoked"})
            rec.message_post(
                body="Expired on %s — the access and its SoD waiver ended with it (role %s)%s."
                % (
                    rec.valid_until,
                    role.code,
                    "; the role stays under %s" % live.source if kept else "",
                )
            )
            self.env["fix.security.audit"].log_event(
                "elevation_expiry",
                "fix.access.request,%d" % rec.id,
                "elevation of %s expired %s: role %s revoked (%d group(s) removed)"
                % (user.login, rec.valid_until, role.code, len(removed)),
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
    tested_on = fields.Date(required=True, default=fields.Date.context_today, readonly=True)
    tested_by_id = fields.Many2one("res.users", string="Tested By", readonly=True)
    users_checked = fields.Integer(readonly=True)
    violations_found = fields.Integer(readonly=True)
    users_in_conflict = fields.Char(string="Conflicting Users", readonly=True)
    result = fields.Selection([("pass", "Pass"), ("fail", "Fail")], readonly=True, index=True)

    def _fix_guarded_fields(self) -> set:
        # the measurement and who took it come from action_run, never typed
        # (M29-3, E21)
        return super()._fix_guarded_fields() | {
            "result",
            "violations_found",
            "users_in_conflict",
            "tested_on",
            "tested_by_id",
            "users_checked",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.result for rec in self.sudo()):
            locked = set(locked) | {"control_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.sod.test") or "SODT/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        # a measured result belongs to the control it measured: re-pointing a
        # pass at a failing control launders it (E21)
        if "control_id" in vals and not self._fix_guard_open():
            for rec in self:
                if rec.result and rec._fix_guard_differs(
                    "control_id", vals["control_id"], rec.control_id
                ):
                    raise UserError("A test that has run stays on its control. File a new run.")
        return super().write(vals)

    def _fix_stamp(self, candidates, offenders):
        self._guarded().write(
            {
                "tested_on": fields.Date.context_today(self),
                "tested_by_id": self.env.uid,
                "users_checked": len(candidates),
                "violations_found": len(offenders),
                "users_in_conflict": ", ".join(offenders.mapped("login"))[:250] or "—",
                "result": "fail" if offenders else "pass",
            }
        )

    def action_run(self):
        """Measures the conflict for real: internal users who hold both roles
        (what was assigned, the employee master and groups that name a role) or,
        for a duty control, both Odoo groups with implied groups counted. Portal
        users are out of scope of the access register. A run is one measurement:
        run again by filing a new row, so the history of results stays."""
        Sod = self.env["fix.sod.control"]
        candidates = (
            self.env["res.users"].sudo().search([("share", "=", False), ("active", "=", True)])
        )
        index = Sod._fix_index()
        conflicts = {user.id: Sod._fix_conflicts(user=user, index=index) for user in candidates}
        for rec in self:
            if rec.result:
                raise UserError("%s has already run. File a new run." % rec.name)
            control = rec.control_id
            if control.control_type == "group":
                # a side that is not installed cannot be measured, and saying
                # so beats reporting a pass
                if not control._fix_pair_groups():
                    raise UserError(
                        "%s cannot be measured: one of its groups is not installed" % control.code
                    )
            elif not (control.role_a_id.sudo().group_ids and control.role_b_id.sudo().group_ids):
                raise UserError(
                    "Both roles on %s need an Odoo group before the test can run" % control.code
                )
            offenders = candidates.filtered(lambda u, c=control: c in conflicts[u.id])
            rec._fix_stamp(candidates, offenders)

    @api.model
    def cron_run_sod_tests(self):
        """E21: the SoD register is measured on a schedule, not when someone
        remembers. One new run per active control that can be measured."""
        if not self.env.su:
            raise AccessError("The scheduled SoD measurement runs from its job only.")
        controls = self.env["fix.sod.control"].search([("active", "=", True)])
        runs = self.create(
            [
                {
                    "control_id": control.id,
                    "company_id": control.company_id.id or self.env.company.id,
                }
                for control in controls.filtered(lambda c: c._fix_pair_groups())
            ]
        )
        runs.action_run()
        return len(runs)


class FixPrivilegedSession(models.Model):
    """Break-glass: request -> a second person approves -> the holder opens it
    (audited, notified) -> closed by the holder or by the clock. The approval
    states what the session may do and until when (E10). Closing records the
    measured duration; the record is the control, it does not itself hand out
    database access."""

    _name = "fix.privileged.session"
    _description = "Privileged Session"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "started_at desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        index=True,
        default=lambda self: self.env.user,
    )
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
    duration_hours = fields.Float(
        string="Hours Needed",
        help="How long the session is needed. Empty means the maximum allowed "
        "(ir.config_parameter %s, default %s hours)."
        % (BREAK_GLASS_PARAM, BREAK_GLASS_DEFAULT_HOURS),
    )
    approver_id = fields.Many2one("res.users", string="Approver", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    decision_note = fields.Char(readonly=True, copy=False)
    expires_at = fields.Datetime(
        string="Expires At",
        readonly=True,
        copy=False,
        help="Set at approval. The session cannot open after it, and an open session is closed "
        "at it by the timeout job.",
    )
    started_at = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
        help="When the request was filed; replaced by the opening time when the session opens.",
    )
    ended_at = fields.Datetime()
    duration_minutes = fields.Integer(readonly=True)
    actions_count = fields.Integer()
    state = fields.Selection(
        [
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("open", "Open"),
            ("closed", "Closed"),
            ("expired", "Approval Lapsed"),
        ],
        required=True,
        default="requested",
        tracking=True,
    )

    _PINNED = ("access_kind", "reason", "ticket_ref", "duration_hours", "company_id")

    def _fix_guarded_fields(self) -> set:
        # the closure stamps the end and the duration is MEASURED (M29-3); who
        # and since when are what the measurement rests on (E11)
        return super()._fix_guarded_fields() | {
            "state",
            "ended_at",
            "duration_minutes",
            "user_id",
            "started_at",
            "approver_id",
            "decided_on",
            "decision_note",
            "expires_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(rec.state != "requested" for rec in self.sudo()):
            locked |= set(self._PINNED)
        return locked

    @api.model
    def _fix_max_hours(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(BREAK_GLASS_PARAM)
        try:
            value = float(raw) if raw else BREAK_GLASS_DEFAULT_HOURS
        except (TypeError, ValueError):
            value = BREAK_GLASS_DEFAULT_HOURS
        return value if value > 0 else BREAK_GLASS_DEFAULT_HOURS

    @api.constrains("duration_hours")
    def _check_duration_hours(self):
        limit = self._fix_max_hours()
        for rec in self:
            if rec.duration_hours < 0 or rec.duration_hours > limit:
                raise ValidationError(
                    "A privileged session may run at most %s hours (%s)."
                    % (limit, BREAK_GLASS_PARAM)
                )

    @api.model_create_multi
    def create(self, vals_list):
        # a session is requested in one's own name only (E60: a plain user
        # opened a db_console session in the admin's name)
        if not self.env.su:
            for vals in vals_list:
                vals.pop("user_id", None)
                vals.pop("started_at", None)
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.privileged.session")
                    or "PS/New"
                )
        records = super().create(vals_list)
        for rec in records.filtered(lambda r: r.state == "requested"):
            rec.sudo()._fix_notify_approvers(
                "Privileged session %s (%s) requested by %s: %s"
                % (rec.name, rec.access_kind, rec.user_id.name, rec.reason)
            )
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            pinned = set(self._PINNED) & set(vals)
            for rec in self:
                changed = [n for n in pinned if rec._fix_guard_differs(n, vals[n], rec[n])]
                if changed and (rec.state != "requested" or rec.user_id != self.env.user):
                    raise UserError(
                        "Only the requester can edit %s, and only before it is decided." % rec.name
                    )
        return super().write(vals)

    def _fix_notify_approvers(self, body, extra=None):
        """A message to the Access Approvers and whoever else must know: opening a
        break-glass session is loud by design."""
        self.ensure_one()
        group = self.env.ref(APPROVER_GROUP, raise_if_not_found=False)
        people = (group.sudo().user_ids if group else self.env["res.users"]) | (
            extra or self.env["res.users"]
        )
        self.message_post(
            body=body,
            partner_ids=people.filtered("active").mapped("partner_id").ids,
            subtype_xmlid="mail.mt_comment",
        )

    def _fix_assert_approver(self):
        user = self.env.user
        if self.env.su:
            return
        if not (user.has_group(APPROVER_GROUP) or user.has_group("base.group_system")):
            raise UserError(
                "Only an Access Approver or a system administrator may decide a privileged "
                "session."
            )
        for rec in self:
            if rec.user_id == user:
                raise UserError("Nobody approves their own privileged session.")

    def action_approve(self):
        self._fix_assert_approver()
        now = fields.Datetime.now().replace(microsecond=0)
        for rec in self:
            if rec.state != "requested":
                raise UserError("Approve a requested session")
            rec.sudo()._guarded().write(
                {
                    "state": "approved",
                    "approver_id": self.env.uid,
                    "decided_on": now,
                    "expires_at": now
                    + timedelta(hours=rec.duration_hours or self._fix_max_hours()),
                }
            )
            self.env["fix.security.audit"].log_event(
                "session_approved",
                "fix.privileged.session,%d" % rec.id,
                "privileged session %s (%s) for %s approved by %s until %s"
                % (
                    rec.name,
                    rec.access_kind,
                    rec.user_id.login,
                    self.env.user.name,
                    rec.expires_at,
                ),
            )

    def action_reject(self, reason=None):
        self._fix_assert_approver()
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why this session is refused.")
        for rec in self:
            if rec.state != "requested":
                raise UserError("Reject a requested session")
            rec.sudo()._guarded().write(
                {
                    "state": "rejected",
                    "approver_id": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                    "decision_note": reason[:250],
                }
            )
            self.env["fix.security.audit"].log_event(
                "session_rejected",
                "fix.privileged.session,%d" % rec.id,
                "privileged session %s refused by %s: %s" % (rec.name, self.env.user.name, reason),
            )

    def action_open(self):
        """The holder opens an approved session before its approval lapses. The
        audit row and the notification are the "loud" part of break-glass."""
        now = fields.Datetime.now().replace(microsecond=0)
        for rec in self:
            if not self.env.su and self.env.user != rec.user_id:
                raise UserError("Only the session's own user (%s) may open it" % rec.user_id.login)
            if rec.state != "approved":
                raise UserError("Only an approved session can open")
            if not rec.expires_at or rec.expires_at < now:
                raise UserError("This approval lapsed at %s. File a new request." % rec.expires_at)
            rec.sudo()._guarded().write({"state": "open", "started_at": now})
            self.env["fix.security.audit"].log_event(
                "session_open",
                "fix.privileged.session,%d" % rec.id,
                "privileged session %s (%s) OPENED by %s, approved by %s, expires %s: %s"
                % (
                    rec.name,
                    rec.access_kind,
                    rec.user_id.login,
                    rec.approver_id.login,
                    rec.expires_at,
                    rec.reason,
                ),
            )
            rec.sudo()._fix_notify_approvers(
                "Privileged session %s (%s) is now OPEN for %s, until %s."
                % (rec.name, rec.access_kind, rec.user_id.name, rec.expires_at),
                extra=rec.approver_id,
            )

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
            rec.sudo()._guarded().write(
                {"state": "closed", "ended_at": now, "duration_minutes": minutes}
            )
            self.env["fix.security.audit"].log_event(
                "privileged",
                "fix.privileged.session,%d" % rec.id,
                "privileged session %s (%s) closed after %d minute(s) by %s"
                % (rec.name, rec.access_kind, minutes, self.env.user.name),
            )

    @api.model
    def cron_close_stale_sessions(self):
        """R3: a privileged session may not stay open forever. Open sessions
        past their expiry or older than the configured timeout are force-closed
        by the cron and the closure is written to the audit trail (loud, not
        silent). An approval nobody used lapses the same way."""
        if not self.env.su:
            raise AccessError("The session timeout runs from its scheduled job only.")
        limit = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("fix_rbac_ext.privileged_session_timeout_minutes", 240)
        )
        now = fields.Datetime.now().replace(microsecond=0)
        cutoff = now - timedelta(minutes=limit)
        stale = self.search(
            [
                ("state", "=", "open"),
                "|",
                ("started_at", "<", cutoff),
                "&",
                ("expires_at", "!=", False),
                ("expires_at", "<", now),
            ]
        )
        for rec in stale:
            minutes = int((now - rec.started_at).total_seconds() // 60)
            rec._guarded().write({"state": "closed", "ended_at": now, "duration_minutes": minutes})
            self.env["fix.security.audit"].log_event(
                "session_timeout",
                "fix.privileged.session,%d" % rec.id,
                "privileged session %s (%s, user %s) FORCE-CLOSED by timeout after %d "
                "minute(s) (limit %d)"
                % (rec.name, rec.access_kind, rec.user_id.login, minutes, limit),
            )
        lapsed = self.search([("state", "=", "approved"), ("expires_at", "<", now)])
        for rec in lapsed:
            rec._guarded().write({"state": "expired"})
            self.env["fix.security.audit"].log_event(
                "session_lapsed",
                "fix.privileged.session,%d" % rec.id,
                "approval of privileged session %s lapsed unused" % rec.name,
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
