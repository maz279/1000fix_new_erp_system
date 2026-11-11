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
import hashlib
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.http import request as http_request

_logger = logging.getLogger(__name__)

GRACE_PARAM = "fix_rbac_ext.certification_grace_days"
SESSION_TIMEOUT_PARAM = "fix_rbac_ext.privileged_session_timeout_minutes"
APPROVER_GROUP = "cd_rbac_ext.group_access_approver"
OFFICER_GROUP = "cd_rbac_ext.group_security_officer"
SYSTEM_GROUP = "base.group_system"


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
        help="Joiner: granted. Leaver: every mapped role is revoked regardless. Mover: this role "
        "is granted and the roles the user was previously assigned are revoked.",
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

    _PINNED = ("event_type", "employee_id", "role_id", "effective_on", "company_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "applied_on", "result_note"}

    def _fix_form_locked_fields(self) -> set:
        # user_id is settled at filing: it may be typed on a new event (an
        # employee with no login), never changed afterwards (E12, E14)
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked.add("user_id")
        if any(rec.state != "pending" for rec in self.sudo()):
            locked |= set(self._PINNED)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.jml.event") or "JML/New"
                )
            # E12: the login affected is the employee's. A typed user is honoured
            # only for a joiner or mover whose employee has no login yet, because
            # naming someone else's login on a leaver deprovisions them.
            if vals.get("employee_id"):
                employee = self.env["hr.employee"].sudo().browse(vals["employee_id"])
                if employee.user_id:
                    vals["user_id"] = employee.user_id.id
                elif vals.get("event_type") == "leaver":
                    vals["user_id"] = False
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            if "user_id" in vals:
                for rec in self:
                    if rec._fix_guard_differs("user_id", vals["user_id"], rec.user_id):
                        raise UserError(
                            "The login an event affects is settled when it is filed. "
                            "File a new event."
                        )
            pinned = set(self._PINNED) & set(vals)
            for rec in self:
                changed = [n for n in pinned if rec._fix_guard_differs(n, vals[n], rec[n])]
                if not changed:
                    continue
                if rec.state != "pending":
                    raise UserError("%s is %s and cannot change." % (rec.name, rec.state))
                if rec.create_uid != self.env.user:
                    raise UserError("Only the person who filed %s can edit it." % rec.name)
        return super().write(vals)

    # ------------------------------------------------------------------
    # Provisioning services (run as sudo AFTER the checks — X1 pattern)
    # ------------------------------------------------------------------

    @api.model
    def _apply_role_grant(self, user, role, source=None, request=None):
        """Record the assignment and grant every Odoo group the role maps to.
        Runs the SoD gate first (A12 R2: all held roles x the new role)."""
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
        # the assignment first: the role is then already accounted for when the
        # res.users doors look at the group write
        self.env["fix.role.assignment"]._fix_record(
            user, role, source or "role grant", request=request
        )
        user.sudo().write({"group_ids": [(4, gid) for gid in groups.ids]})
        user.invalidate_recordset(["group_ids"])
        return groups

    @api.model
    def _apply_role_revoke(self, user, role, reason=None):
        """End the role's assignment and remove its groups, EXCEPT groups
        another role the user was ACTUALLY given also requires (A12 R1, E3).
        A role merely sharing a group with this one keeps nothing."""
        Sod = self.env["fix.sod.control"]
        groups = Sod._role_groups(role)
        if not groups:
            raise UserError("Role %s maps to no Odoo group, so it cannot be revoked" % role.code)
        employees = Sod._fix_user_employees(user) or self.env["hr.employee"]
        self.env["fix.role.assignment"]._fix_live(user, role)._fix_end(
            reason or "role %s revoked" % role.code
        )
        # the employee master's copy goes too, or the role would still be "held"
        for emp in employees.sudo():
            if "additional_role_ids" in emp._fields and role in emp.additional_role_ids:
                emp.write({"additional_role_ids": [(3, role.id)]})
            if "primary_role_id" in emp._fields and emp.primary_role_id == role:
                emp.write({"primary_role_id": False})
        # what the rest of the user's access still names once these groups are gone
        standing = Sod._fix_standing_role_ids(user) - {role.id}
        rest = set(user.sudo().group_ids.ids) - set(groups.ids)
        rest -= Sod._fix_explained_groups(standing)
        others = (standing | Sod._fix_infer_role_ids(rest)) - {role.id}
        still_required = self.env["fix.role"].sudo().browse(sorted(others)).mapped("group_ids")
        removable = groups - still_required
        if removable:
            user.sudo().write({"group_ids": [(3, gid) for gid in removable.ids]})
            user.invalidate_recordset(["group_ids"])
        return removable

    @api.model
    def _deprovision_user(self, user, source):
        """X2 / BRU-SEC-06: a leaver loses EVERYTHING — all groups (not only
        role-mapped ones), every assignment, API keys, sessions and the login
        itself. Records the audit row."""
        user = user.sudo()
        groups_before = user.group_ids
        self.env["fix.role.assignment"]._fix_live(user)._fix_end("leaver: %s" % source)
        keys = self.env["res.users.apikeys"].sudo().search([("user_id", "=", user.id)])
        key_count = len(keys)
        keys.unlink()
        try:
            with self.env.cr.savepoint():
                user.device_ids._revoke()
        except Exception as exc:  # no session store in a cron: archiving still stops logins
            _logger.info("leaver %s: session revoke skipped (%s)", user.login, exc)
        user.write({"group_ids": [(5, 0, 0)], "active": False})
        user.invalidate_recordset(["group_ids"])
        self.env["fix.security.audit"].log_event(
            "leaver",
            "res.users,%d" % user.id,
            "leaver deprovisioned (%s): %d group(s) removed (%s), %d API key(s) removed, "
            "login deactivated"
            % (
                source,
                len(groups_before),
                ", ".join(groups_before.mapped("name"))[:120] or "none",
                key_count,
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

    def _fix_leaver_keeps_login(self):
        """Why this leaver must not touch the login, or False. Mirrors the M21
        consumer: root and admin stay, and a login another still-employed
        record uses stays."""
        self.ensure_one()
        user = self.user_id.sudo()
        if user in (self.env.ref("base.user_root"), self.env.ref("base.user_admin")):
            return "protected login"
        Employee = self.env["hr.employee"].sudo()
        domain = [("user_id", "=", user.id), ("id", "!=", self.employee_id.id)]
        if "left_date" in Employee._fields:
            domain.append(("left_date", "=", False))
        if Employee.search_count(domain):
            return "login shared with a still-employed record"
        return False

    # ------------------------------------------------------------------
    # The employee.left consumer (A12 X2, P2 hand-off M21 -> M29)
    # ------------------------------------------------------------------

    @api.model
    def consume_employee_left(self, event):
        """fix.event.consumer target for `employee.left` (cd_employee_core
        publishes it through the transactional outbox; the relay calls this
        as superuser). Idempotent: a second delivery for an already
        deprovisioned employee is a no-op.

        Superuser only (E1): a plain user reaching this over JSON-RPC stripped
        any colleague. The event is also not believed on its own: the employee
        must really have left. A future leaving date stays pending on the JML
        screen until it is due."""
        if not self.env.su:
            raise AccessError("The leaver consumer runs from the event relay only.")
        payload = event.get("payload") or {}
        employee_id = payload.get("employee_id") or event.get("aggregate_id")
        employee = self.env["hr.employee"].sudo().browse(int(employee_id or 0)).exists()
        if not employee:
            return True
        left_date = employee.left_date if "left_date" in employee._fields else False
        if employee.active and not left_date:
            _logger.warning("employee.left for %s who has not left: ignored", employee.id)
            return True
        already = self.sudo().search(
            [
                ("event_type", "=", "leaver"),
                ("employee_id", "=", employee.id),
                ("state", "in", ("applied", "pending")),
            ],
            limit=1,
        )
        if already:
            return True
        jml = self.sudo().create(
            {
                "event_type": "leaver",
                "employee_id": employee.id,
                "effective_on": left_date or payload.get("left_date") or fields.Date.today(),
                "company_id": employee.company_id.id or self.env.company.id,
            }
        )
        if jml.effective_on > fields.Date.context_today(self):
            return True  # due later: the pending row is the reminder
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
        if self.env.user.has_group(APPROVER_GROUP):
            return
        raise UserError(
            "Only an Access Approver (cd_rbac_ext.group_access_approver) or an "
            "Access Rights administrator may apply a JML event."
        )

    def _assert_second_person(self):
        """E12: JML is a grant path, so it carries the two-person rule of the
        request path: the person applying neither filed the event nor benefits."""
        if self.env.su:
            return
        for rec in self.sudo():
            if self.env.user in (rec.user_id, rec.create_uid):
                raise UserError(
                    "%s must be applied by a second person: not the person it affects and not "
                    "the person who filed it." % rec.name
                )

    def action_apply(self):
        """Real effect on res.users.group_ids: joiners/movers get the role's
        groups after the SoD gate; a leaver loses EVERY group and the login."""
        self._assert_apply_authority()
        self._assert_second_person()
        today = fields.Date.context_today(self)
        audit = self.env["fix.security.audit"]
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending JML event can be applied")
            user = rec.user_id.sudo()
            if not user:
                raise UserError("The employee has no linked user, so no access can change")
            if rec.event_type == "leaver":
                if rec.effective_on > today:
                    raise UserError(
                        "This leaver takes effect on %s. Apply it on that date." % rec.effective_on
                    )
                kept = rec._fix_leaver_keeps_login()
                assets = self._unassign_itsm_assets(rec.employee_id)
                if kept:
                    note = "leaver applied, access kept (%s): %d ITSM asset(s) unassigned" % (
                        kept,
                        assets,
                    )
                    audit.log_event("leaver_kept", "res.users,%d" % user.id, note)
                else:
                    count = self._deprovision_user(user, "jml %s" % rec.name)
                    note = (
                        "leaver applied: %d group(s) removed, login deactivated, "
                        "%d ITSM asset(s) unassigned" % (count, assets)
                    )
            else:
                if not rec.role_id:
                    raise UserError("Pick a role for a %s event" % rec.event_type)
                was_inactive = not user.active
                groups = self._apply_role_grant(
                    user, rec.role_id, source="fix.jml.event,%d" % rec.id
                )
                note = "%s granted (%s)" % (rec.role_id.code, ", ".join(groups.mapped("name")))
                if was_inactive:
                    user.write({"active": True})
                    note += "; login reactivated"
                if rec.event_type == "mover":
                    # E24: a move ends the old job's access. The new role is
                    # already assigned, so groups it shares are kept.
                    previous = (
                        self.env["fix.role.assignment"]._fix_live(user).mapped("role_id")
                        - rec.role_id
                    )
                    for role in previous:
                        self._apply_role_revoke(user, role, "mover %s" % rec.name)
                    if previous:
                        note += "; previous role(s) revoked: %s" % ", ".join(
                            previous.mapped("code")
                        )
                audit.log_event(rec.event_type, "fix.jml.event,%d" % rec.id, note)
            rec._guarded().write(
                {"state": "applied", "applied_on": fields.Datetime.now(), "result_note": note[:250]}
            )

    def action_cancel(self):
        self._assert_apply_authority()
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending event can be cancelled")
            rec._guarded().write({"state": "cancelled"})


class FixAccessCertificationCampaign(models.Model):
    """One review period: generates a locked line per user and role held, each
    assigned to the employee's manager (E17). The line, not this record, is what
    keeps or removes access."""

    _name = "fix.access.certification.campaign"
    _description = "Access Certification Campaign"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    period = fields.Char(required=True, help="Review period, e.g. 2026-Q4")
    due_on = fields.Date(
        string="Due On",
        required=True,
        default=lambda self: fields.Date.context_today(self)
        + timedelta(days=int(self.env["ir.config_parameter"].sudo().get_param(GRACE_PARAM, 14))),
        help="Lines still pending after this date are revoked by the close-out job.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("generated", "Generated")],
        required=True,
        default="draft",
        tracking=True,
    )
    generated_on = fields.Datetime(readonly=True)
    generated_by_id = fields.Many2one("res.users", string="Generated By", readonly=True)
    line_ids = fields.One2many("fix.access.certification", "campaign_id", string="Lines")
    line_count = fields.Integer(string="Lines", compute="_compute_counts")
    pending_count = fields.Integer(string="Pending", compute="_compute_counts")
    no_reviewer_note = fields.Char(
        string="Skipped (no reviewer)",
        readonly=True,
        help="Users with no reviewer available: no manager with a login, and no other Access "
        "Approver. Appoint one and generate a new campaign.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "generated_on",
            "generated_by_id",
            "no_reviewer_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(rec.state != "draft" for rec in self.sudo()):
            locked |= {"period", "due_on", "company_id"}
        return locked

    @api.depends("line_ids", "line_ids.decision")
    def _compute_counts(self):
        for rec in self:
            lines = rec.sudo().line_ids
            rec.line_count = len(lines)
            rec.pending_count = len(lines.filtered(lambda line: line.decision == "pending"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = "Certification %s" % (vals.get("period") or "")
        return super().create(vals_list)

    def action_generate(self):
        """Lines per internal user and held role, for this company. Runs as a
        service after the check: the generator needs no rights over users."""
        if not (
            self.env.su
            or self.env.user.has_group(APPROVER_GROUP)
            or self.env.user.has_group("base.group_erp_manager")
        ):
            raise UserError(
                "Only an Access Approver or an Access Rights administrator may run a "
                "certification campaign."
            )
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s has already been generated." % rec.name)
            created, skipped = (
                self.env["fix.access.certification"].sudo()._fix_generate_campaign_lines(rec.sudo())
            )
            rec.sudo()._guarded().write(
                {
                    "state": "generated",
                    "generated_on": fields.Datetime.now(),
                    "generated_by_id": self.env.uid,
                    "no_reviewer_note": ", ".join(sorted(skipped))[:250] or False,
                }
            )
            self.env["fix.security.audit"].log_event(
                "certification_campaign",
                "fix.access.certification.campaign,%d" % rec.id,
                "campaign %s generated by %s: %d line(s), %d user(s) with no reviewer"
                % (rec.period, self.env.user.name, created, len(skipped)),
            )
        return {"note": "%d line(s) generated" % sum(self.sudo().mapped("line_count"))}


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
    campaign_id = fields.Many2one(
        "fix.access.certification.campaign", string="Campaign", index=True, ondelete="set null"
    )
    user_id = fields.Many2one("res.users", string="User Under Review", required=True, index=True)
    role_id = fields.Many2one("fix.role", string="Role Held", required=True, index=True)
    reviewer_id = fields.Many2one(
        "res.users",
        string="Reviewer",
        help="The user's manager; if there is none, an Access Approver. Never the user under "
        "review. Locked once the line exists.",
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

    _PINNED = ("user_id", "role_id", "reviewer_id", "campaign_id")
    _FROZEN = ("period", "due_on", "note", "company_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"decision", "decided_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked |= set(self._PINNED)
        if any(rec.decision != "pending" for rec in self.sudo()):
            locked |= set(self._FROZEN)
        return locked

    @api.model
    def _fix_resolve_reviewer(self, user):
        """E17: the user's manager; failing that, an Access Approver. Never the
        reviewed user, and never someone who cannot log in."""
        employees = self.env["hr.employee"].sudo().search([("user_id", "=", user.id)])
        for manager in employees.mapped("parent_id.user_id"):
            if manager != user and manager.active:
                return manager
        group = self.env.ref(APPROVER_GROUP, raise_if_not_found=False)
        members = group.sudo().user_ids if group else self.env["res.users"]
        others = members.filtered(lambda u: u.active and u != user).sorted("id")
        return others[:1]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._fix_refuse_past_due(vals)
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.access.certification")
                    or "CERT/New"
                )
            if not vals.get("reviewer_id") and vals.get("user_id"):
                reviewer = self._fix_resolve_reviewer(self.env["res.users"].browse(vals["user_id"]))
                if not reviewer:
                    raise ValidationError(
                        "This user has no manager with a login and there is no other Access "
                        "Approver to review the line."
                    )
                vals["reviewer_id"] = reviewer.id
        return super().create(vals_list)

    def write(self, vals):
        self._fix_refuse_past_due(vals)
        if not self._fix_guard_open():
            pinned = set(self._PINNED) & set(vals)
            frozen = set(self._FROZEN) & set(vals)
            for rec in self:
                if [n for n in pinned if rec._fix_guard_differs(n, vals[n], rec[n])]:
                    raise UserError(
                        "A certification line stays on its user, role and reviewer once it exists."
                    )
                if rec.decision != "pending" and [
                    n for n in frozen if rec._fix_guard_differs(n, vals[n], rec[n])
                ]:
                    raise UserError("A decided certification line cannot change.")
        return super().write(vals)

    @api.constrains("user_id", "reviewer_id")
    def _check_reviewer_not_reviewed(self):
        for rec in self:
            if rec.reviewer_id and rec.reviewer_id == rec.user_id:
                raise ValidationError(
                    "The reviewer may not be the user under review (self-certification)."
                )

    @api.constrains("user_id", "role_id")
    def _check_role_is_held(self):
        Sod = self.env["fix.sod.control"]
        for rec in self:
            if not Sod.user_holds_role(rec.user_id, rec.role_id):
                raise ValidationError(
                    "%s does not hold %s: a certification line reviews access someone has."
                    % (rec.user_id.sudo().login, rec.role_id.code)
                )

    def _fix_refuse_past_due(self, vals):
        # a line due in the past is a line the close-out cron revokes unreviewed
        # (constraints run as superuser, so this cannot be one: seeds and tests may)
        due_on = vals.get("due_on")
        if (
            due_on
            and not self._fix_guard_open()
            and fields.Date.to_date(due_on) < fields.Date.context_today(self)
        ):
            raise ValidationError("A certification line cannot be due in the past.")

    @api.model
    def _fix_generate_campaign_lines(self, campaign):
        """Service body of the campaign action: (lines created, logins skipped)."""
        if not self.env.su:
            raise AccessError("Certification lines are generated by a campaign.")
        Sod = self.env["fix.sod.control"]
        users = (
            self.env["res.users"]
            .sudo()
            .search(
                [
                    ("share", "=", False),
                    ("active", "=", True),
                    ("company_ids", "in", campaign.company_id.id),
                ]
            )
        )
        created = 0
        skipped = set()
        for user in users:
            roles = Sod.user_held_roles(user)
            if not roles:
                continue
            reviewer = self._fix_resolve_reviewer(user)
            if not reviewer:
                skipped.add(user.login)
                continue
            for role in roles:
                if self.search_count(
                    [
                        ("period", "=", campaign.period),
                        ("user_id", "=", user.id),
                        ("role_id", "=", role.id),
                        ("company_id", "=", campaign.company_id.id),
                    ]
                ):
                    continue
                line = self.create(
                    {
                        "period": campaign.period,
                        "campaign_id": campaign.id,
                        "company_id": campaign.company_id.id,
                        "user_id": user.id,
                        "role_id": role.id,
                        "reviewer_id": reviewer.id,
                        "due_on": campaign.due_on,
                    }
                )
                line.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=campaign.due_on,
                    summary="Certify %s for %s" % (role.code, user.login),
                    user_id=reviewer.id,
                )
                created += 1
        return created, skipped

    def _assert_reviewer(self):
        """M29-7: only the ASSIGNED reviewer decides this line (or the
        superuser / close-out cron), and never the reviewed user."""
        for rec in self:
            if self.env.su:
                continue
            if self.env.user != rec.reviewer_id:
                raise UserError(
                    "This certification line is assigned to %s; only that reviewer decides it."
                    % (rec.reviewer_id.name or "nobody")
                )
            if self.env.user == rec.user_id:
                raise UserError("Nobody certifies their own access.")

    def _fix_close_activity(self):
        self.sudo().activity_ids.unlink()

    def action_certify(self):
        """Certify = keep the access. The SoD gate runs here too (R2): a
        reviewer may not certify access that now conflicts with what the user
        holds — they must revoke instead."""
        self._assert_reviewer()
        for rec in self:
            if rec.decision != "pending":
                raise UserError("This access line is already decided")
            Sod = self.env["fix.sod.control"]
            Sod.check_user_assignment(rec.user_id, rec.role_id)
            # A08 S4: keeping a role whose groups sit on one side of a duty
            # conflict the user holds needs a live SoD exception; otherwise
            # the reviewer revokes. Strict, as the reviewer may be sudo.
            index = Sod._fix_index()
            role_groups = Sod._role_groups(rec.role_id).sudo().all_implied_ids
            duty_conflicts = (
                Sod._fix_conflicts(user=rec.user_id, index=index)
                .filtered(lambda c: c.control_type == "group")
                .filtered(lambda c, rg=role_groups: set(c._fix_pair_groups() or ()) & set(rg))
            )
            Sod._fix_enforce(
                rec.user_id,
                Sod.browse(),
                duty_conflicts,
                "role %s certified" % rec.role_id.code,
                strict=True,
            )
            # the reviewer holds no write right on the register (E4): the
            # check above is what authorises this
            rec.sudo()._guarded().write(
                {"decision": "certified", "decided_on": fields.Datetime.now()}
            )
            rec._fix_close_activity()
            self.env["fix.security.audit"].log_event(
                "certification",
                "fix.access.certification,%d" % rec.id,
                "access certified (kept): %s keeps %s for %s by %s"
                % (rec.user_id.sudo().login, rec.role_id.code, rec.period, self.env.user.name),
            )

    def action_revoke(self):
        """Removes the role's groups from the user. The business check runs
        as the reviewer; the group change runs as a service, so a
        manager-reviewer without Access Rights can still revoke (M29-7/E52)."""
        self._assert_reviewer()
        for rec in self:
            if rec.decision != "pending":
                raise UserError("This access line is already decided")
            removed = self.env["fix.jml.event"]._apply_role_revoke(
                rec.user_id, rec.role_id, "certification %s" % rec.name
            )
            rec.sudo()._guarded().write(
                {"decision": "revoked", "decided_on": fields.Datetime.now()}
            )
            rec._fix_close_activity()
            self.env["fix.security.audit"].log_event(
                "certification",
                "fix.access.certification,%d" % rec.id,
                "access revoked on review: %s loses %s group(s) for %s by %s"
                % (rec.user_id.sudo().login, len(removed), rec.period, self.env.user.name),
            )

    @api.model
    def cron_close_certifications(self):
        """R3 / FR-SEC-026: unconfirmed access is revoked automatically. Any
        line still pending past its due date is revoked by the close-out."""
        if not self.env.su:
            raise AccessError("The certification close-out runs from its scheduled job only.")
        today = fields.Date.today()
        overdue = self.search([("decision", "=", "pending"), ("due_on", "<", today)])
        for rec in overdue:
            removed = 0
            mapped = self.env["fix.sod.control"]._role_groups(rec.role_id)
            if rec.user_id.active and mapped:
                removed_groups = self.env["fix.jml.event"]._apply_role_revoke(
                    rec.user_id, rec.role_id, "certification %s lapsed" % rec.name
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
            rec._fix_close_activity()
            self.env["fix.security.audit"].log_event(
                "certification",
                "fix.access.certification,%d" % rec.id,
                "close-out: unconfirmed access %s / %s revoked for %s (due %s)"
                % (rec.user_id.login, rec.role_id.code, rec.period, rec.due_on),
            )
        return len(overdue)


class FixEncryptionKey(models.Model):
    """A register of vault REFERENCES. Nothing here calls a vault (there is none
    on this estate yet): a rotation records what the custodian did in the secret
    manager, and a vault:// reference is checked for form only."""

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
    # E19: where a key lives is for its custodians, not for every employee.
    vault_ref = fields.Char(
        string="Vault Reference",
        required=True,
        groups="cd_rbac_ext.group_key_custodian,base.group_system",
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
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked |= {"vault_ref", "custodian_id", "successor_id"}
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self.sudo():
                if "vault_ref" in vals and rec.vault_ref != vals["vault_ref"]:
                    raise UserError(
                        "A key's vault reference changes only through Rotate, which retires "
                        "this key, registers the successor and writes the audit row."
                    )
                if "custodian_id" in vals and rec._fix_guard_differs(
                    "custodian_id", vals["custodian_id"], rec.custodian_id
                ):
                    self.env["fix.security.audit"].log_event(
                        "key_custodian_change",
                        "fix.encryption.key,%d" % rec.id,
                        "custodian of %s changed by %s" % (rec.code, self.env.user.name),
                    )
        return super().write(vals)

    @api.constrains("vault_ref")
    def _check_vault_ref(self):
        for rec in self.sudo():
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
        """Registers a rotation the custodian performed in the secret manager:
        the successor reference becomes the active key with the rotation clock,
        the old key is retired and a `key_rotation` audit row is written. The
        material itself lives in the vault — this register never sees it
        (SEC-101), and no vault is contacted to confirm the path."""
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
            today = fields.Date.today()
            next_due = today + timedelta(days=365 // max(rec.rotations_per_year, 1))
            successor = Key._guarded().create(
                {
                    "code": "%s/V%d" % (rec.code, same_prefix + 1),
                    "name": "%s (rotated %s)" % (rec.name, today),
                    "company_id": rec.company_id.id,
                    "purpose": rec.purpose,
                    "algorithm": rec.algorithm,
                    "vault_ref": ref,
                    "rotations_per_year": rec.rotations_per_year,
                    "custodian_id": rec.custodian_id.id or self.env.uid,
                    "state": "active",
                    # the clock belongs on the key now in use (E19)
                    "last_rotated_on": today,
                    "next_rotation_on": next_due,
                }
            )
            rec._guarded().write(
                {
                    "state": "retired",
                    "last_rotated_on": today,
                    "next_rotation_on": False,
                    "successor_id": successor.id,
                }
            )
            # the audit trail is readable by every employee: no vault paths in it
            self.env["fix.security.audit"].log_event(
                "key_rotation",
                "fix.encryption.key,%d" % rec.id,
                "key %s rotated into %s by %s" % (rec.code, successor.code, self.env.user.name),
            )


class FixSecurityAuditAnchor(models.Model):
    """The chain's high-water mark, and the seal over rows written before the
    current hash format. Only the audit trail writes it. A row deleted off the
    tail leaves the anchor ahead of the table; concurrent appenders serialise on
    this row, which is also what stops the chain forking."""

    _name = "fix.security.audit.anchor"
    _description = "Security Audit Chain Anchor"

    head_sequence = fields.Integer(readonly=True)
    head_hash = fields.Char(readonly=True)
    legacy_through = fields.Integer(
        readonly=True, help="Rows up to this sequence predate the current hash format."
    )
    legacy_digest = fields.Char(readonly=True, help="Seal over those rows, taken at migration.")
    anchored_on = fields.Datetime(readonly=True)

    @api.model
    def _fix_get(self):
        anchor = self.sudo().search([], limit=1)
        return anchor or self.sudo().create({"anchored_on": fields.Datetime.now()})


class FixSecurityAudit(models.Model):
    """Append-only, hash-chained, and SYSTEM-WRITTEN (A12 R5): the actor,
    the time, the sequence and both hashes are set by the server and refuse
    caller-supplied values. No user ACL carries create — code appends rows
    through log_event(). Entries carry a hash chain over (previous hash,
    payload) so a deleted or edited row breaks the chain — that is what
    "immutable" means here, since a database trigger cannot be relied on
    from the workspace.

    Hash formats (E20): 2 is current and covers the sequence and IP address too.
    Rows older than the migration keep the format they were written in and are
    reported as legacy, never rewritten: 1 can still be recomputed; 0 (the early
    seed rows) cannot, so those rows are held by their chain links and by the
    seal the migration took over them."""

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
    hash_version = fields.Integer(string="Hash Format", readonly=True, default=2)
    # Presentation only (fix_real UI walk, 11 Nov 2026): object_ref stores the
    # technical "model,id" the hash covers, which read as raw text on M29-audit.
    # This resolves it for display; it is never stored, so the chain is untouched.
    object_label = fields.Char(
        string="Object", compute="_compute_object_label", search="_search_object_label"
    )

    def _search_object_label(self, operator, value):
        # Quick Find keeps matching the stored reference it used to search
        return [("object_ref", operator, value)]

    @api.depends("object_ref")
    def _compute_object_label(self):
        models_by_name = {}
        for rec in self:
            ref = (rec.object_ref or "").strip()
            model, _sep, rid = ref.partition(",")
            if model not in models_by_name:
                ir_model = self.env["ir.model"]._get(model) if model in self.env else False
                models_by_name[model] = ir_model.name if ir_model else False
            label = models_by_name[model]
            if not label:
                rec.object_label = ref
                continue
            if not rid.strip().isdigit():
                rec.object_label = label
                continue
            target = self.env[model].browse(int(rid))
            try:
                name = target.exists() and target.display_name
            except AccessError:
                name = False
            rec.object_label = "%s: %s" % (label, name) if name else "%s #%s" % (label, rid.strip())

    # fields only the server may set; create() strips them from any caller
    _SYSTEM_SET = (
        "sequence",
        "occurred_at",
        "actor_id",
        "ip_address",
        "prev_hash",
        "entry_hash",
        "hash_version",
    )

    @staticmethod
    def _plain(value):
        if hasattr(value, "strftime"):  # datetime: hash the stored precision
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return str(value or "")

    def _hash_payload(self, vals, prev_hash):
        """Format 1, for the rows that were written with it."""
        raw = "|".join(
            [
                prev_hash or "",
                self._plain(vals.get("event")),
                self._plain(vals.get("object_ref")),
                self._plain(vals.get("detail")),
                self._plain(vals.get("actor_id")),
                self._plain(vals.get("occurred_at")),
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _hash_payload_v2(self, vals, prev_hash):
        raw = "|".join(
            [
                "2",
                prev_hash or "",
                self._plain(vals.get("sequence")),
                self._plain(vals.get("event")),
                self._plain(vals.get("object_ref")),
                self._plain(vals.get("detail")),
                self._plain(vals.get("actor_id")),
                self._plain(vals.get("occurred_at")),
                self._plain(vals.get("ip_address")),
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @api.private
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
        computed here. Returns the row.

        @api.private (E18): server code appends, a JSON-RPC caller cannot."""
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
        self.check_access("create")
        ip_address = http_request.httprequest.remote_addr if http_request else False
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
            vals["ip_address"] = ip_address
        anchor = self.env["fix.security.audit.anchor"]._fix_get()
        self.env.cr.execute(
            "SELECT id FROM fix_security_audit_anchor WHERE id = %s FOR UPDATE", [anchor.id]
        )
        last = self.sudo().search([], order="sequence desc, id desc", limit=1)
        prev_hash = last.entry_hash or ""
        seq = last.sequence or 0
        for vals in vals_list:
            seq += 1
            vals["sequence"] = seq
            vals["prev_hash"] = prev_hash
            vals["hash_version"] = 2
            vals["entry_hash"] = self._hash_payload_v2(vals, prev_hash)
            prev_hash = vals["entry_hash"]
        rows = super().create(vals_list)
        anchor.write({"head_sequence": seq, "head_hash": prev_hash})
        anchor.flush_recordset()
        return rows

    def write(self, vals):
        raise UserError("The security audit trail is append-only — entries cannot be edited")

    def unlink(self):
        raise UserError("The security audit trail is append-only — entries cannot be deleted")

    @api.model
    def _fix_legacy_digest(self, rows):
        """A seal over rows the current format does not cover."""
        digest = hashlib.sha256()
        for rec in rows:
            digest.update(
                "|".join(
                    self._plain(v)
                    for v in (
                        rec.sequence,
                        rec.hash_version,
                        rec.event,
                        rec.object_ref,
                        rec.detail,
                        rec.actor_id.id,
                        rec.occurred_at,
                        rec.ip_address,
                        rec.prev_hash,
                        rec.entry_hash,
                    )
                ).encode("utf-8")
            )
        return digest.hexdigest()

    @api.model
    def _fix_anchor_chain(self):
        """The migration entry (E20). The early seed rows hash under a formula
        nothing can reproduce, so a verifier reported them as tampering. History
        is not rewritten: each existing row is labelled with the format it
        recomputes under, the set is sealed, and this anchoring is itself a row
        on the chain. Idempotent."""
        if not self.env.su:
            raise AccessError("The audit chain is anchored by the migration only.")
        anchor = self.env["fix.security.audit.anchor"]._fix_get()
        if anchor.legacy_digest:
            return anchor
        rows = self.search([], order="sequence asc, id asc")
        counts = {0: 0, 1: 0}
        prev = ""
        for rec in rows:
            ok = (rec.entry_hash or "") == self._hash_payload(
                {
                    "event": rec.event,
                    "object_ref": rec.object_ref,
                    "detail": rec.detail,
                    "actor_id": rec.actor_id.id or "",
                    "occurred_at": rec.occurred_at,
                },
                prev,
            )
            version = 1 if ok else 0
            counts[version] += 1
            self.env.cr.execute(
                "UPDATE fix_security_audit SET hash_version = %s WHERE id = %s", [version, rec.id]
            )
            prev = rec.entry_hash or ""
        self.invalidate_model(["hash_version"])
        digest = self._fix_legacy_digest(rows)
        anchor.write(
            {
                "legacy_through": rows[-1:].sequence or 0,
                "legacy_digest": digest,
                "anchored_on": fields.Datetime.now(),
                "head_sequence": rows[-1:].sequence or 0,
                "head_hash": rows[-1:].entry_hash or "",
            }
        )
        self.log_event(
            "audit.chain_anchor",
            "fix.security.audit.anchor,%d" % anchor.id,
            "chain anchored at sequence %d: %d row(s) in the early seed format, %d in format 1, "
            "sealed %s" % (anchor.legacy_through, counts[0], counts[1], digest[:16]),
        )
        return anchor

    def _fix_chain_report(self):
        """(rows checked, legacy rows, discontinuities, what they are)."""
        rows = self.sudo().search([], order="sequence asc, id asc")
        anchor = self.env["fix.security.audit.anchor"]._fix_get()
        broken = legacy = 0
        notes = []
        prev = ""
        for rec in rows:
            payload = {
                "event": rec.event,
                "object_ref": rec.object_ref,
                "detail": rec.detail,
                "actor_id": rec.actor_id.id or "",
                "occurred_at": rec.occurred_at,
            }
            if rec.sequence > anchor.legacy_through:
                payload.update(sequence=rec.sequence, ip_address=rec.ip_address)
                expected = self._hash_payload_v2(payload, prev)
                hash_ok = rec.hash_version == 2 and rec.entry_hash == expected
            else:
                legacy += 1
                # format 0 cannot be recomputed: its link and the seal hold it
                hash_ok = rec.hash_version == 0 or rec.entry_hash == self._hash_payload(
                    payload, prev
                )
            if (rec.prev_hash or "") != prev or not hash_ok:
                broken += 1
                notes.append("sequence %d" % rec.sequence)
            prev = rec.entry_hash or ""
        if anchor.legacy_digest and anchor.legacy_digest != self._fix_legacy_digest(
            rows.filtered(lambda r: r.sequence <= anchor.legacy_through)
        ):
            broken += 1
            notes.append("the seal over the legacy rows")
        head = rows[-1:]
        if (head.sequence or 0) != anchor.head_sequence or (head.entry_hash or "") != (
            anchor.head_hash or ""
        ):
            broken += 1
            notes.append("the tail (the anchor records sequence %d)" % anchor.head_sequence)
        return len(rows), legacy, broken, notes

    def action_verify_chain(self):
        """Recomputes every row's hash from its stored payload, checks the
        prev_hash links, the seal over legacy-format rows and the high-water mark
        (R5, E20). A clean chain is a result to show, a broken one a refusal."""
        total, legacy, broken, notes = self._fix_chain_report()
        summary = "Chain verified: %d entr(ies), %d discontinuity(ies), %d legacy-format" % (
            total,
            broken,
            legacy,
        )
        if broken:
            raise UserError("%s: %s" % (summary, "; ".join(notes)[:300]))
        return {"note": summary}


class FixSecurityIncident(models.Model):
    """Anyone may report an incident and read what they reported. Handling it,
    and reading anyone else's, is for a Security Officer (E16: the breach
    assessment names data subjects; it is not for every employee)."""

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
    severity_pending = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        string="Severity Proposed",
        readonly=True,
        copy=False,
        help="A proposed change, in force only once a second person confirms it.",
    )
    severity_proposed_by_id = fields.Many2one(
        "res.users", string="Severity Proposed By", readonly=True, copy=False
    )
    detected_at = fields.Datetime(required=True, default=fields.Datetime.now)
    detected_by_id = fields.Many2one(
        "res.users", string="Detected By", default=lambda self: self.env.user
    )
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

    _NARRATIVE = (
        "title",
        "category",
        "detected_at",
        "detected_by_id",
        "affected_user_id",
        "session_id",
        "description",
        "containment",
        "root_cause",
        "breach_assessment",
    )

    def _fix_guarded_fields(self) -> set:
        # state and resolution time only through contain/close. Severity is not
        # here because a reporter sets it at filing (E15); write() guards it after.
        return super()._fix_guarded_fields() | {
            "state",
            "resolved_on",
            "severity_pending",
            "severity_proposed_by_id",
            "severity_set_by_id",
            "severity_confirmed_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        # reads through sudo: the workspace asks before it knows the caller may see the row
        locked = set(super()._fix_form_locked_fields())
        records = self.sudo()
        if records:
            locked.add("severity")
        if any(rec.state == "closed" for rec in records):
            locked |= set(self._NARRATIVE)
        if any(rec.category == "data_leak" for rec in records):
            locked.add("category")
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.security.incident")
                    or "SEC/New"
                )
        # the stamp is the server's: a typed "set by" is not who set it
        records = super().create(vals_list)
        records.sudo()._guarded().write({"severity_set_by_id": self.env.uid})
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self.sudo():
                if "severity" in vals and rec.severity != vals["severity"]:
                    raise UserError(
                        "Severity changes through Set Severity, confirmed by a second person."
                    )
                if rec.state == "closed" and [
                    n
                    for n in set(self._NARRATIVE) & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]:
                    raise UserError("%s is closed: its record cannot change." % rec.name)
                if "category" in vals and rec.category != vals["category"]:
                    # recategorising a leak would dodge the breach assessment (E16)
                    if rec.category == "data_leak":
                        raise UserError(
                            "A data-leak incident stays a data leak. If it proves not to be one, "
                            "the breach assessment says so."
                        )
                    self.env["fix.security.audit"].log_event(
                        "incident",
                        "fix.security.incident,%d" % rec.id,
                        "category %s -> %s by %s"
                        % (rec.category, vals["category"], self.env.user.name),
                    )
        return super().write(vals)

    def _assert_officer(self):
        user = self.env.user
        if not (self.env.su or user.has_group(OFFICER_GROUP) or user.has_group(SYSTEM_GROUP)):
            raise UserError(
                "Only a Security Officer (cd_rbac_ext.group_security_officer) handles an incident."
            )

    def action_contain(self):
        self._assert_officer()
        for rec in self:
            if rec.state != "open":
                raise UserError("Contain an open incident")
            if len((rec.containment or "").strip()) < 20:
                raise UserError(
                    "Record what was done to contain the incident first (at least a "
                    "sentence — a marker like 'x' is not containment)"
                )
            rec._guarded().write({"state": "contained"})
            self.env["fix.security.audit"].log_event(
                "incident",
                "fix.security.incident,%d" % rec.id,
                "incident contained: %s (%s) by %s" % (rec.name, rec.severity, self.env.user.name),
            )

    def action_close(self):
        """§8.3: close needs containment, a root cause and (for a data leak)
        a breach assessment; the resolution time is stamped here, never
        typed. Writes the audit row."""
        self._assert_officer()
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
                % (rec.name, rec.severity, resolved_on, self.env.user.name),
            )

    def action_set_severity(self, severity=None, confirmed_by_id=None):
        """R5: a severity change is a two-person control. This proposes it; a
        DIFFERENT Security Officer applies it with Confirm Severity. Naming a
        witness has no effect (`confirmed_by_id` is ignored): the witness acts
        himself or nothing changes (E15)."""
        self._assert_officer()
        valid = {key for key, _lbl in type(self).severity.selection}
        severity = (severity or "").strip().lower()
        if severity not in valid:
            raise UserError("Severity must be one of %s" % ", ".join(sorted(valid)))
        for rec in self:
            if rec.state == "closed":
                raise UserError("%s is closed: its record cannot change." % rec.name)
            rec._guarded().write(
                {"severity_pending": severity, "severity_proposed_by_id": self.env.uid}
            )
            self.env["fix.security.audit"].log_event(
                "incident",
                "fix.security.incident,%d" % rec.id,
                "severity %s -> %s proposed by %s" % (rec.severity, severity, self.env.user.name),
            )

    def action_confirm_severity(self):
        """The second person's act: only now does the severity change."""
        self._assert_officer()
        for rec in self:
            if not rec.severity_pending:
                raise UserError("No severity change is waiting on %s." % rec.name)
            if rec.severity_proposed_by_id == self.env.user and not self.env.su:
                raise UserError("A second person must confirm the change you proposed.")
            old, new = rec.severity, rec.severity_pending
            proposer = rec.severity_proposed_by_id
            rec._guarded().write(
                {
                    "severity": new,
                    "severity_set_by_id": proposer.id,
                    "severity_confirmed_by_id": self.env.uid,
                    "severity_pending": False,
                    "severity_proposed_by_id": False,
                }
            )
            self.env["fix.security.audit"].log_event(
                "incident",
                "fix.security.incident,%d" % rec.id,
                "severity %s -> %s proposed by %s, confirmed by %s"
                % (old, new, proposer.name, self.env.user.name),
            )

    def action_reject_severity(self):
        self._assert_officer()
        for rec in self:
            if not rec.severity_pending:
                raise UserError("No severity change is waiting on %s." % rec.name)
            proposed = rec.severity_pending
            rec._guarded().write({"severity_pending": False, "severity_proposed_by_id": False})
            self.env["fix.security.audit"].log_event(
                "incident",
                "fix.security.incident,%d" % rec.id,
                "severity change to %s not confirmed by %s" % (proposed, self.env.user.name),
            )
