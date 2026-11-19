# M29 second capture pass (19 Nov 2026): the spec records the sub-module pages
# still could not capture after the 14 Nov pass.
#
# Spec: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_*.md
#   p1 Identity & MFA   §8.1 Active -> Suspended -> Active (`identity.suspended`,
#                       /identities/{id}/suspend); FR-SEC-012 service accounts
#                       with an accountable human owner; BRU-SEC-17 / AUT-SEC-11
#                       orphaned accounts; AUT-SEC-25 credential rotation;
#                       AUT-SEC-03 a leaver's devices deregistered and delegated
#                       authority reassigned.
#   p6 Data Protection  FR-SEC-047: a RESIDENCY classification on every field,
#                       with the owning module and who classified it.
#   p7 Monitoring       §8.3 / AUT-SEC-13 / NFR-094: the breach assessment as a
#                       decision (personal data? notifiable?), the §13 rule that
#                       the triager is never the sole approver of "not
#                       notifiable", and the hand-off to M60; FR-SEC-034/035,
#                       BRU-SEC-20, AUT-SEC-10: a real emergency break-glass path
#                       (open first, justify after, reviewed by someone else) and
#                       the session's recorded actions; AUT-SEC-16 / AC-26: a
#                       penetration-test engagement tracked to verified closure.
#
# Every lifecycle stamp is guarded (fix.guarded.mixin); outcomes go to the
# hash-chained fix.security.audit trail, which every internal user reads, so the
# audit rows carry references and categories, never personal data.
import datetime
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_access_ops import local_today

_logger = logging.getLogger(__name__)

APPROVER_GROUP = "cd_rbac_ext.group_access_approver"
OFFICER_GROUP = "cd_rbac_ext.group_security_officer"
SYSTEM_GROUP = "base.group_system"
ERP_MANAGER_GROUP = "base.group_erp_manager"

BREAK_GLASS_HOURS_PARAM = "fix_rbac_ext.break_glass_hours"
BREAK_GLASS_HOURS_DEFAULT = 4.0
JUSTIFY_HOURS_PARAM = "fix_rbac_ext.break_glass_justification_hours"
JUSTIFY_HOURS_DEFAULT = 24
BREACH_SLA_HOURS_PARAM = "fix_rbac_ext.breach_assessment_hours"
BREACH_SLA_HOURS_DEFAULT = 72
ORPHAN_GRACE_HOURS = 24  # BRU-SEC-17: "more than 24 hours"
ROTATION_WARN_DAYS = 7


def _param_number(env, key, default):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    try:
        value = float(raw) if raw else float(default)
    except (TypeError, ValueError):
        value = float(default)
    return value if value > 0 else float(default)


def _people(env, *xmlids):
    users = env["res.users"]
    for xmlid in xmlids:
        group = env.ref(xmlid, raise_if_not_found=False)
        if group:
            users |= group.sudo().user_ids
    return users.filtered(lambda u: u.active and not u.share)


def _is_any(env, *xmlids):
    if env.su:
        return True
    return any(env.user.has_group(x) for x in xmlids)


# ---------------------------------------------------------------------------
# p1: suspend / reinstate an identity (§8.1), and the leaver hand-offs
# ---------------------------------------------------------------------------
class FixJmlEventSuspension(models.Model):
    _inherit = "fix.jml.event"

    event_type = fields.Selection(
        selection_add=[("suspend", "Suspend"), ("reinstate", "Reinstate")],
        ondelete={"suspend": "cascade", "reinstate": "cascade"},
    )
    suspend_reason = fields.Selection(
        [
            ("leave", "Extended leave"),
            ("investigation", "Investigation"),
            ("certification", "Access certification not confirmed"),
            ("security", "Security concern / compromised account"),
            ("other", "Other"),
        ],
        string="Suspension Reason",
        help="§8.1: why the identity is suspended. Required for a suspension.",
    )

    _SUSPENSION = ("suspend", "reinstate")

    @api.constrains("event_type", "suspend_reason", "reason")
    def _check_suspension_terms(self):
        for rec in self:
            if rec.event_type == "suspend" and not rec.suspend_reason:
                raise ValidationError("Say why the identity is suspended.")
            if rec.event_type in self._SUSPENSION and len((rec.reason or "").strip()) < 10:
                raise ValidationError(
                    "A %s needs a written justification (at least a short sentence)."
                    % dict(self._fields["event_type"].selection)[rec.event_type].lower()
                )

    @api.model_create_multi
    def create(self, vals_list):
        # the login a suspension affects is the employee's own, never a typed
        # one (the E12 leaver rule): an employee with no login has nothing to suspend
        Employee = self.env["hr.employee"].sudo()
        for vals in vals_list:
            if vals.get("event_type") in self._SUSPENSION and vals.get("employee_id"):
                employee = Employee.browse(vals["employee_id"])
                vals["user_id"] = employee.user_id.id or False
                if not employee.user_id:
                    raise UserError(
                        "%s has no login, so there is no access to %s."
                        % (employee.name, vals["event_type"])
                    )
        return super().create(vals_list)

    @api.depends(
        "event_type",
        "employee_id",
        "user_id",
        "role_id",
        "extra_role_ids",
        "operating_unit_ids",
        "default_operating_unit_id",
        "permission_line_ids.level",
        "permission_line_ids.can_approve",
        "permission_line_ids.can_print",
        "permission_line_ids.can_export",
        "permission_line_ids.can_email",
    )
    def _compute_access_preview(self):
        super()._compute_access_preview()
        for rec in self.filtered(lambda r: r.event_type in self._SUSPENSION):
            login = rec.user_id.sudo().login or rec.employee_id.sudo().user_id.login or "-"
            if rec.event_type == "suspend":
                rec.permission_preview = (
                    "Suspend %s: the login is switched off and every open session ends on the "
                    "effective date. Roles, groups and records are kept, so a reinstatement "
                    "restores exactly this access." % login
                )
            else:
                rec.permission_preview = (
                    "Reinstate %s: the login suspended by the last suspension is switched back "
                    "on, with the roles it held. A leaver or an expired access comes back only "
                    "through a joiner." % login
                )

    def action_apply(self):
        special = self.filtered(lambda r: r.event_type in self._SUSPENSION)
        rest = self - special
        if rest:
            super(FixJmlEventSuspension, rest).action_apply()
        if special:
            special._fix_apply_suspension()
        return True

    def _fix_last_identity_event(self, user):
        return self.sudo().search(
            [
                ("user_id", "=", user.id),
                ("state", "=", "applied"),
                ("event_type", "in", ("joiner", "mover", "leaver", "suspend", "reinstate")),
            ],
            order="applied_on desc, id desc",
            limit=1,
        )

    def _fix_apply_suspension(self):
        self._assert_apply_authority()
        self._assert_second_person()
        today = fields.Date.context_today(self)
        audit = self.env["fix.security.audit"]
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending JML event can be applied")
            if rec.effective_on > today:
                raise UserError(
                    "%s takes effect on %s. Apply it on that date." % (rec.name, rec.effective_on)
                )
            user = rec.user_id.sudo() or rec.employee_id.sudo().user_id
            if not user:
                raise UserError("The employee has no login, so no access can change.")
            if rec.event_type == "suspend":
                if user in (self.env.ref("base.user_root"), self.env.ref("base.user_admin")):
                    raise UserError("The administrator login is never suspended.")
                if not user.active:
                    raise UserError("%s is already inactive." % user.login)
                try:
                    with self.env.cr.savepoint():
                        user.device_ids._revoke()
                except Exception as exc:  # no session store in a cron or test
                    _logger.info("suspend %s: session revoke skipped (%s)", user.login, exc)
                user.write({"active": False})
                note = (
                    "identity suspended (%s): login switched off, sessions ended, %d group(s) kept"
                    % (
                        rec.suspend_reason,
                        len(user.group_ids),
                    )
                )
                audit.log_event("identity.suspended", "res.users,%d" % user.id, note)
            else:
                if user.active:
                    raise UserError("%s is active: there is nothing to reinstate." % user.login)
                last = rec._fix_last_identity_event(user)
                if not last or last.event_type != "suspend":
                    raise UserError(
                        "%s was not switched off by a suspension (%s). A leaver or an expired "
                        "access comes back through a joiner event."
                        % (user.login, last.event_type if last else "no suspension on record")
                    )
                employee = rec.employee_id.sudo()
                left = employee.left_date if "left_date" in employee._fields else False
                if not employee.active or left:
                    raise UserError(
                        "%s has left: a leaver is not reinstated." % (employee.name or user.login)
                    )
                expires = (
                    user.fix_access_expires_on if "fix_access_expires_on" in user._fields else False
                )
                if expires and expires < today:
                    raise UserError(
                        "%s's access ended on %s. Extend it through a mover or joiner event."
                        % (user.login, expires)
                    )
                user.write({"active": True})
                note = "identity reinstated after %s: login switched on with %d group(s)" % (
                    last.name,
                    len(user.group_ids),
                )
                audit.log_event("identity.reinstated", "res.users,%d" % user.id, note)
            rec._guarded().write(
                {"state": "applied", "applied_on": fields.Datetime.now(), "result_note": note[:250]}
            )

    # AUT-SEC-03: a leaver's devices are deregistered and the authority others
    # delegated to them (or they delegated) ends. Every leaver path - applied
    # event, employee.left consumer, leaver with no login - runs this hand-off.
    @api.model
    def _unassign_itsm_assets(self, employee):
        count = super()._unassign_itsm_assets(employee)
        self._fix_revoke_leaver_devices(employee)
        self._fix_end_leaver_delegations(employee)
        return count

    @api.model
    def _fix_revoke_leaver_devices(self, employee):
        if "fix.technician.device" not in self.env:
            return 0
        devices = (
            self.env["fix.technician.device"]
            .sudo()
            .search([("employee_id", "=", employee.id), ("state", "=", "enrolled")])
        )
        if devices:
            devices.write(
                {
                    "state": "revoked",
                    "revoke_reason": "departed",
                    "revoke_notes": "Deregistered by the leaver hand-off (AUT-SEC-03).",
                    "revoked_at": fields.Datetime.now(),
                    "revoked_by_id": self.env.uid,
                }
            )
            self.env["fix.security.audit"].log_event(
                "leaver_devices",
                "hr.employee,%d" % employee.id,
                "%d technician device(s) deregistered on leaver" % len(devices),
            )
        return len(devices)

    @api.model
    def _fix_end_leaver_delegations(self, employee):
        if "fix.approval.substitution" not in self.env:
            return 0
        subs = (
            self.env["fix.approval.substitution"]
            .sudo()
            .search(
                [
                    ("state", "in", ("draft", "active")),
                    "|",
                    ("delegate_id", "=", employee.id),
                    ("absent_approver_id", "=", employee.id),
                ]
            )
        )
        for sub in subs:
            sub._guarded().write({"state": "expired", "expired_by_id": self.env.uid})
        if subs:
            self.env["fix.security.audit"].log_event(
                "leaver_delegations",
                "hr.employee,%d" % employee.id,
                "%d delegation(s) ended on leaver: %s"
                % (len(subs), ", ".join(subs.mapped("name"))),
            )
        return len(subs)


# ---------------------------------------------------------------------------
# p1: service accounts (FR-SEC-012, BRU-SEC-17, AUT-SEC-11, AUT-SEC-25)
# ---------------------------------------------------------------------------
class FixServiceAccount(models.Model):
    """A non-human identity: an integration login, scheduler or API client. It
    always has an accountable human owner, a stated scope and a credential held
    in the vault (the reference only, never the secret), rotated on a schedule.
    An account whose owner is gone is orphaned: flagged at once and suspended
    after 24 hours (BRU-SEC-17)."""

    _name = "fix.service.account"
    _description = "Service Account"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, name"

    name = fields.Char(string="Account Name", required=True, tracking=True)
    code = fields.Char(string="Reference", readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    kind = fields.Selection(
        [
            ("integration", "Integration / connector"),
            ("api_client", "API client"),
            ("scheduler", "Scheduled job / robot"),
            ("monitoring", "Monitoring / backup agent"),
            ("other", "Other"),
        ],
        required=True,
        default="integration",
    )
    purpose = fields.Text(required=True, help="What the account exists to do.")
    scopes = fields.Text(
        string="Permitted Scope",
        required=True,
        help="The systems, endpoints or models the credential may reach - and nothing else.",
    )
    user_id = fields.Many2one(
        "res.users",
        string="Technical Login",
        index=True,
        help="The Odoo login the account signs in with, if it has one. Suspending or "
        "retiring the account switches it off.",
    )
    consumer_ref = fields.Char(
        string="API Consumer / Client ID", help="The M28 API consumer or the client id it uses."
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Accountable Owner",
        required=True,
        tracking=True,
        index=True,
        help="The person answerable for the account (FR-SEC-012).",
    )
    credential_ref = fields.Char(
        string="Credential Vault Reference",
        required=True,
        help="vault://... - the reference only; the secret never enters this database.",
    )
    rotation_days = fields.Integer(string="Rotate Every (days)", default=90, required=True)
    last_rotated_on = fields.Date(string="Last Rotated On", readonly=True)
    next_rotation_on = fields.Date(
        string="Next Rotation Due", compute="_compute_next_rotation", store=True
    )
    rotation_alerted_on = fields.Date(readonly=True)
    orphan_flagged_on = fields.Datetime(string="Orphan Flagged On", readonly=True)
    is_orphaned = fields.Boolean(string="Orphaned", compute="_compute_is_orphaned")
    state = fields.Selection(
        [("active", "Active"), ("suspended", "Suspended"), ("retired", "Retired")],
        required=True,
        default="active",
        tracking=True,
    )
    state_note = fields.Char(string="Last Status Change", readonly=True)
    state_changed_by_id = fields.Many2one("res.users", string="Changed By", readonly=True)

    @api.depends("last_rotated_on", "rotation_days", "create_date")
    def _compute_next_rotation(self):
        for rec in self:
            base = rec.last_rotated_on or (rec.create_date and rec.create_date.date())
            rec.next_rotation_on = (
                base + datetime.timedelta(days=max(rec.rotation_days, 1)) if base else False
            )

    def _compute_is_orphaned(self):
        for rec in self:
            rec.is_orphaned = bool(rec.state == "active" and rec._fix_orphan_reason())

    def _fix_orphan_reason(self):
        owner = self.sudo().owner_id
        if not owner or not owner.active:
            return "the owner's login is inactive"
        if owner.share:
            return "the owner is not an internal user"
        employees = owner.employee_ids if "employee_ids" in owner._fields else False
        if employees and not employees.filtered(
            lambda e: e.active and not (e.left_date if "left_date" in e._fields else False)
        ):
            return "the owner has left"
        return ""

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "code",
            "last_rotated_on",
            "rotation_alerted_on",
            "orphan_flagged_on",
            "state_note",
            "state_changed_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            # the credential changes only through Register Rotation
            locked.add("credential_ref")
        if any(rec.state == "retired" for rec in self.sudo()):
            locked |= {"name", "kind", "purpose", "scopes", "user_id", "consumer_ref", "owner_id"}
        return locked

    @staticmethod
    def _fix_check_vault(ref):
        ref = (ref or "").strip()
        if not ref.startswith("vault://") or len(ref) < 12:
            raise ValidationError(
                "The credential is held in the vault: give its reference (vault://...), "
                "never the secret itself."
            )
        return ref

    def _fix_assert_admin(self):
        if not _is_any(self.env, OFFICER_GROUP, APPROVER_GROUP, SYSTEM_GROUP):
            raise UserError(
                "Only a Security Officer, an Access Approver or a system administrator manages "
                "service accounts."
            )

    @api.constrains("owner_id", "user_id")
    def _check_owner(self):
        for rec in self.sudo():
            if rec.user_id and rec.owner_id == rec.user_id:
                raise ValidationError(
                    "A service account cannot own itself: name the accountable person."
                )
            if rec.state == "active" and (not rec.owner_id.active or rec.owner_id.share):
                raise ValidationError(
                    "The owner of %s must be an active internal user (FR-SEC-012)." % rec.name
                )

    @api.constrains("user_id", "state")
    def _check_one_account_per_login(self):
        for rec in self.filtered(lambda r: r.user_id and r.state != "retired"):
            twin = self.sudo().search_count(
                [("id", "!=", rec.id), ("user_id", "=", rec.user_id.id), ("state", "!=", "retired")]
            )
            if twin:
                raise ValidationError(
                    "%s is already registered as a service account." % rec.user_id.login
                )

    @api.constrains("rotation_days")
    def _check_rotation_days(self):
        for rec in self:
            if not 1 <= rec.rotation_days <= 366:
                raise ValidationError("Rotate a credential at least once a year (1-366 days).")

    @api.model_create_multi
    def create(self, vals_list):
        self._fix_assert_admin()
        for vals in vals_list:
            vals["credential_ref"] = self._fix_check_vault(vals.get("credential_ref"))
            vals.pop("last_rotated_on", None)
        records = super().create(vals_list)
        for rec in records:
            rec.sudo()._guarded().write(
                {
                    "code": self.env["ir.sequence"].sudo().next_by_code("fix.service.account")
                    or "SVC/New"
                }
            )
            self.env["fix.security.audit"].log_event(
                "service_account",
                "fix.service.account,%d" % rec.id,
                "service account %s registered, owner %s" % (rec.code, rec.owner_id.login),
            )
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            if "credential_ref" in vals and any(
                rec._fix_guard_differs("credential_ref", vals["credential_ref"], rec.credential_ref)
                for rec in self
            ):
                raise UserError("The credential reference changes through Register Rotation.")
            if set(vals) & {"owner_id", "scopes", "user_id"}:
                self._fix_assert_admin()
                for rec in self:
                    if "owner_id" in vals and rec._fix_guard_differs(
                        "owner_id", vals["owner_id"], rec.owner_id
                    ):
                        self.env["fix.security.audit"].log_event(
                            "service_account",
                            "fix.service.account,%d" % rec.id,
                            "service account %s owner changed by %s"
                            % (rec.code, self.env.user.login),
                        )
        res = super().write(vals)
        if "owner_id" in vals:
            self.sudo()._guarded().write({"orphan_flagged_on": False})
        return res

    def _fix_set_state(self, state, note, login_active):
        for rec in self:
            rec.sudo()._guarded().write(
                {"state": state, "state_note": note[:250], "state_changed_by_id": self.env.uid}
            )
            if rec.sudo().user_id:
                rec.sudo().user_id.write({"active": login_active})
            self.env["fix.security.audit"].log_event(
                "service_account",
                "fix.service.account,%d" % rec.id,
                "service account %s %s: %s" % (rec.code, state, note[:120]),
            )

    def action_register_rotation(self, new_vault_ref=None):
        """AUT-SEC-25: the owner (or an officer) records a rotation done in the vault."""
        ref = self._fix_check_vault(new_vault_ref)
        for rec in self:
            if rec.state != "active":
                raise UserError("%s is %s: rotate an active account." % (rec.code, rec.state))
            if not (
                self.env.user == rec.sudo().owner_id
                or _is_any(self.env, OFFICER_GROUP, SYSTEM_GROUP)
            ):
                raise UserError("Only the owner or a Security Officer registers a rotation.")
            if ref == rec.sudo().credential_ref:
                raise UserError("A rotation gives a NEW vault reference.")
            rec.sudo()._guarded().write(
                {
                    "credential_ref": ref,
                    "last_rotated_on": local_today(self),
                    "rotation_alerted_on": False,
                }
            )
            self.env["fix.security.audit"].log_event(
                "service_account",
                "fix.service.account,%d" % rec.id,
                "service account %s credential rotated by %s" % (rec.code, self.env.user.login),
            )
        return True

    def action_suspend(self, reason=None):
        self._fix_assert_admin()
        reason = (reason or "").strip()
        if len(reason) < 10:
            raise UserError("Say why the account is suspended.")
        for rec in self:
            if rec.state != "active":
                raise UserError("%s is %s." % (rec.code, rec.state))
        self._fix_set_state("suspended", reason, False)
        return True

    def action_reactivate(self):
        self._fix_assert_admin()
        for rec in self:
            if rec.state != "suspended":
                raise UserError("Only a suspended account is reactivated.")
            if not self.env.su and rec.state_changed_by_id == self.env.user:
                raise UserError(
                    "%s must be reactivated by a second person, not the one who suspended it."
                    % rec.code
                )
            why = rec._fix_orphan_reason()
            if why:
                raise UserError(
                    "%s cannot come back: %s. Name a new owner first." % (rec.code, why)
                )
        self._fix_set_state("active", "reactivated by %s" % self.env.user.login, True)
        return True

    def action_retire(self, reason=None):
        self._fix_assert_admin()
        reason = (reason or "").strip()
        if len(reason) < 10:
            raise UserError("Say why the account is retired.")
        for rec in self:
            if rec.state == "retired":
                raise UserError("%s is already retired." % rec.code)
        self._fix_set_state("retired", reason, False)
        return True

    @api.model
    def _cron_service_account_watch(self):
        """Daily. BRU-SEC-17 / AUT-SEC-11: an active account without an active
        owner is flagged, and suspended once flagged for 24 hours. AUT-SEC-25:
        the owner is reminded when a rotation falls due."""
        now = fields.Datetime.now()
        today = local_today(self)
        officers = _people(self.env, OFFICER_GROUP) or _people(self.env, SYSTEM_GROUP)
        suspended = 0
        for rec in self.sudo().search([("state", "=", "active")]):
            why = rec._fix_orphan_reason()
            if not why:
                if rec.orphan_flagged_on:
                    rec._guarded().write({"orphan_flagged_on": False})
            elif not rec.orphan_flagged_on:
                rec._guarded().write({"orphan_flagged_on": now})
                for user in officers:
                    rec.activity_schedule(
                        "mail.mail_activity_data_todo",
                        user_id=user.id,
                        summary="Orphaned service account %s: name a new owner" % rec.code,
                    )
                self.env["fix.security.audit"].log_event(
                    "service_account.orphaned",
                    "fix.service.account,%d" % rec.id,
                    "service account %s has no active owner (%s)" % (rec.code, why),
                )
            elif now - rec.orphan_flagged_on >= datetime.timedelta(hours=ORPHAN_GRACE_HOURS):
                rec._fix_set_state(
                    "suspended", "orphaned for 24 hours: %s (BRU-SEC-17)" % why, False
                )
                suspended += 1
            if (
                rec.state == "active"
                and rec.next_rotation_on
                and rec.next_rotation_on <= today + datetime.timedelta(days=ROTATION_WARN_DAYS)
                and rec.rotation_alerted_on != rec.next_rotation_on
                and rec.owner_id.active
            ):
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=rec.owner_id.id,
                    date_deadline=rec.next_rotation_on,
                    summary="Rotate the credential of %s by %s" % (rec.code, rec.next_rotation_on),
                )
                rec._guarded().write({"rotation_alerted_on": rec.next_rotation_on})
        return suspended


# ---------------------------------------------------------------------------
# p6: the residency classification on every field (FR-SEC-047, NFR-086a)
# ---------------------------------------------------------------------------
class FixSensitiveFieldResidency(models.Model):
    _name = "fix.sensitive.field"
    _inherit = ["fix.sensitive.field", "fix.guarded.mixin"]

    residency_class = fields.Selection(
        [
            ("none", "Not residency-classified"),
            ("resident", "Bangladesh-resident (NFR-086)"),
            ("restricted", "Restricted data (localised)"),
            ("cii", "Critical information infrastructure"),
        ],
        string="Residency Class",
        required=True,
        default="none",
        help="FR-SEC-047: where the value may be stored. A residency-classified field "
        "is written to the resident store only and never transferred across a border "
        "without an approved transfer (M60).",
    )
    owning_module = fields.Char(
        string="Owning Module", help="The module that owns the field, e.g. M21 or M33."
    )
    classified_by_id = fields.Many2one("res.users", string="Classified By", readonly=True)
    classified_on = fields.Datetime(string="Classified On", readonly=True)

    _CLASSIFICATION = ("sensitivity", "data_class", "residency_class", "masking_rule")

    @api.constrains("residency_class", "sensitivity")
    def _check_residency_sensitivity(self):
        for rec in self:
            if rec.residency_class != "none" and rec.sensitivity in ("s0", "s1"):
                raise ValidationError(
                    "%s.%s is residency-classified, so it is at least S2 - Confidential."
                    % (rec.model_name, rec.field_name)
                )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"classified_by_id", "classified_on"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.pop("classified_by_id", None)
            vals.pop("classified_on", None)
        records = super().create(vals_list)
        records.sudo()._guarded().write(
            {"classified_by_id": self.env.uid, "classified_on": fields.Datetime.now()}
        )
        return records

    def write(self, vals):
        changed = set(self._CLASSIFICATION) & set(vals)
        res = super().write(vals)
        if changed and not self._fix_guard_open():
            self.sudo()._guarded().write(
                {"classified_by_id": self.env.uid, "classified_on": fields.Datetime.now()}
            )
            for rec in self:
                self.env["fix.security.audit"].log_event(
                    "classification",
                    "fix.sensitive.field,%d" % rec.id,
                    "%s.%s reclassified (%s) by %s"
                    % (
                        rec.model_name,
                        rec.field_name,
                        ", ".join(sorted(changed)),
                        self.env.user.login,
                    ),
                )
        return res


# ---------------------------------------------------------------------------
# p7: the breach assessment as a decision, handed to M60 (§8.3, AUT-SEC-13)
# ---------------------------------------------------------------------------
class FixSecurityIncidentBreach(models.Model):
    _inherit = "fix.security.incident"

    owner_id = fields.Many2one(
        "res.users", string="Incident Owner", tracking=True, help="§10.1: the officer who runs it."
    )
    personal_data_involved = fields.Selection(
        [("unknown", "Not known yet"), ("no", "No"), ("yes", "Yes")],
        string="Personal Data Involved?",
        required=True,
        default="unknown",
        tracking=True,
        help="NFR-094: an incident involving personal data needs a breach assessment.",
    )
    significant_damage_likely = fields.Boolean(
        string="Significant Damage Likely?",
        help="Is significant harm to the data subjects likely? A yes makes it notifiable.",
    )
    data_subjects_estimate = fields.Integer(string="Data Subjects Affected (estimate)")
    breach_decision = fields.Selection(
        [("notifiable", "Notifiable"), ("not_notifiable", "Not notifiable")],
        string="Breach Decision",
        readonly=True,
        copy=False,
    )
    breach_assessed_by_id = fields.Many2one("res.users", string="Assessed By", readonly=True)
    breach_assessed_on = fields.Datetime(string="Assessed On", readonly=True)
    breach_confirmed_by_id = fields.Many2one(
        "res.users", string="'Not Notifiable' Confirmed By", readonly=True
    )
    breach_confirmed_on = fields.Datetime(string="Confirmed On", readonly=True)
    statutory_clock_start = fields.Datetime(string="Statutory Clock Started", readonly=True)
    m60_notification_ref = fields.Char(string="M60 Breach Record", readonly=True)
    breach_assessment_due = fields.Datetime(
        string="Assessment Due", compute="_compute_breach_due", store=True
    )
    breach_overdue = fields.Boolean(string="Assessment Overdue", compute="_compute_breach_overdue")

    @api.depends("detected_at", "personal_data_involved")
    def _compute_breach_due(self):
        hours = _param_number(self.env, BREACH_SLA_HOURS_PARAM, BREACH_SLA_HOURS_DEFAULT)
        for rec in self:
            rec.breach_assessment_due = (
                rec.detected_at + datetime.timedelta(hours=hours)
                if rec.detected_at and rec.personal_data_involved == "yes"
                else False
            )

    def _compute_breach_overdue(self):
        now = fields.Datetime.now()
        for rec in self:
            rec.breach_overdue = bool(
                rec.personal_data_involved == "yes"
                and not rec._fix_breach_settled()
                and rec.breach_assessment_due
                and rec.breach_assessment_due < now
            )

    def _fix_breach_settled(self):
        self.ensure_one()
        if self.breach_decision == "notifiable":
            return True
        return bool(self.breach_decision == "not_notifiable" and self.breach_confirmed_by_id)

    _BREACH_STAMPS = (
        "breach_decision",
        "breach_assessed_by_id",
        "breach_assessed_on",
        "breach_confirmed_by_id",
        "breach_confirmed_on",
        "statutory_clock_start",
        "m60_notification_ref",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self._BREACH_STAMPS)

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(rec.breach_decision for rec in self.sudo()):
            locked |= {
                "personal_data_involved",
                "significant_damage_likely",
                "data_subjects_estimate",
            }
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            facts = {
                "personal_data_involved",
                "significant_damage_likely",
                "data_subjects_estimate",
            }
            for rec in self.sudo():
                if rec.breach_decision and [
                    n for n in facts & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])
                ]:
                    raise UserError(
                        "%s has been assessed: the breach facts cannot change." % rec.name
                    )
        res = super().write(vals)
        if vals.get("personal_data_involved") == "yes":
            self._fix_ask_for_assessment()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.filtered(lambda r: r.personal_data_involved == "yes")._fix_ask_for_assessment()
        return records

    def _fix_ask_for_assessment(self):
        """AUT-SEC-13: personal data involved -> the officers owe a breach assessment."""
        officers = _people(self.env, OFFICER_GROUP)
        for rec in self.sudo().filtered(lambda r: not r.breach_decision):
            for user in rec.owner_id or officers:
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=user.id,
                    date_deadline=rec.breach_assessment_due and rec.breach_assessment_due.date(),
                    summary="Breach assessment due for %s (personal data involved)" % rec.name,
                )

    def action_assess_breach(self, decision=None):
        """The officer's decision: notifiable starts the statutory clock and hands
        the breach to M60; not notifiable waits for a second officer's confirmation
        (§13: the triager is never the sole approver of 'not notifiable')."""
        self._assert_officer()
        key = (decision or "").strip().lower().replace(" ", "_").replace("-", "_")
        key = {"yes": "notifiable", "no": "not_notifiable", "not": "not_notifiable"}.get(key, key)
        if key not in ("notifiable", "not_notifiable"):
            raise UserError("The decision is 'notifiable' or 'not notifiable'.")
        audit = self.env["fix.security.audit"]
        for rec in self:
            if rec.state == "closed":
                raise UserError("%s is closed." % rec.name)
            if rec.personal_data_involved != "yes":
                raise UserError(
                    "Record that personal data is involved before assessing a breach of %s."
                    % rec.name
                )
            if rec.breach_decision == "notifiable":
                raise UserError("%s is already notifiable and handed to M60." % rec.name)
            if rec.breach_decision == "not_notifiable" and rec.breach_confirmed_by_id:
                raise UserError("%s was confirmed not notifiable." % rec.name)
            if len((rec.breach_assessment or "").strip()) < 20:
                raise UserError(
                    "Write the breach assessment first: whose data, how much, and the likely harm."
                )
            if key == "not_notifiable" and rec.significant_damage_likely:
                raise UserError(
                    "Significant damage is likely, so %s is notifiable (NFR-094)." % rec.name
                )
            now = fields.Datetime.now()
            vals = {
                "breach_decision": key,
                "breach_assessed_by_id": self.env.uid,
                "breach_assessed_on": now,
                "breach_confirmed_by_id": False,
                "breach_confirmed_on": False,
            }
            if key == "notifiable":
                vals["statutory_clock_start"] = now
            rec._guarded().write(vals)
            if key == "notifiable":
                ref = rec._fix_breach_handoff()
                rec._guarded().write({"m60_notification_ref": ref or False})
                if not ref:
                    rec.message_post(
                        body="Notifiable breach: M60 is not installed, so notify the Compliance "
                        "Officer directly. The statutory clock started at %s." % now
                    )
            audit.log_event(
                "security.breach_assessed",
                "fix.security.incident,%d" % rec.id,
                "%s assessed %s by %s%s"
                % (
                    rec.name,
                    key.replace("_", " "),
                    self.env.user.login,
                    (", handed to M60 as %s" % rec.m60_notification_ref)
                    if rec.m60_notification_ref
                    else "",
                ),
            )
        return True

    def action_confirm_not_notifiable(self):
        self._assert_officer()
        for rec in self:
            if rec.breach_decision != "not_notifiable" or rec.breach_confirmed_by_id:
                raise UserError("%s has no 'not notifiable' decision waiting." % rec.name)
            if not self.env.su and rec.breach_assessed_by_id == self.env.user:
                raise UserError(
                    "A second Security Officer confirms 'not notifiable', not the one who "
                    "assessed it."
                )
            rec._guarded().write(
                {
                    "breach_confirmed_by_id": self.env.uid,
                    "breach_confirmed_on": fields.Datetime.now(),
                }
            )
            self.env["fix.security.audit"].log_event(
                "security.breach_assessed",
                "fix.security.incident,%d" % rec.id,
                "%s 'not notifiable' confirmed by %s" % (rec.name, self.env.user.login),
            )
        return True

    def _fix_breach_handoff(self):
        """Hand the notifiable breach to M60 (overridden by cd_grc). Returns the
        M60 record reference, or False when M60 is not installed."""
        return False

    def action_close(self):
        for rec in self:
            if rec.state != "contained":
                continue  # the base action says why
            if rec.personal_data_involved == "unknown":
                raise UserError(
                    "State whether personal data is involved before closing %s." % rec.name
                )
            if rec.personal_data_involved == "yes" and not rec._fix_breach_settled():
                raise UserError(
                    "%s involves personal data: complete the breach assessment (and, for 'not "
                    "notifiable', a second officer's confirmation) before closing." % rec.name
                )
        return super().action_close()


# ---------------------------------------------------------------------------
# p7: emergency break-glass, the session's recorded actions and its review
# ---------------------------------------------------------------------------
class FixPrivilegedSessionBreakGlass(models.Model):
    _inherit = "fix.privileged.session"

    break_glass = fields.Boolean(
        string="Emergency Break-Glass",
        help="FR-SEC-035: open at once without prior approval. Loud: every Access "
        "Approver, Security Officer and administrator is told immediately, a written "
        "justification is due afterwards and someone else reviews it.",
    )
    actions_summary = fields.Text(
        string="Actions Taken",
        help="FR-SEC-034: what was done in the session. Required to close it.",
    )
    justification = fields.Text(string="Post-hoc Justification", readonly=True)
    justification_due_at = fields.Datetime(string="Justification Due", readonly=True)
    justification_escalated_on = fields.Datetime(readonly=True)
    reviewed_by_id = fields.Many2one("res.users", string="Reviewed By", readonly=True)
    reviewed_on = fields.Datetime(string="Reviewed On", readonly=True)
    review_outcome = fields.Selection(
        [("justified", "Justified"), ("misuse", "Not justified")],
        string="Review Outcome",
        readonly=True,
    )
    review_note = fields.Char(string="Review Note", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "justification",
            "justification_due_at",
            "justification_escalated_on",
            "reviewed_by_id",
            "reviewed_on",
            "review_outcome",
            "review_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(rec.state != "requested" for rec in self.sudo()):
            locked.add("break_glass")
        if any(rec.state == "closed" for rec in self.sudo()):
            locked.add("actions_summary")
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self.sudo():
                if (
                    "break_glass" in vals
                    and rec.state != "requested"
                    and bool(vals["break_glass"]) != rec.break_glass
                ):
                    raise UserError("Break-glass is chosen when the session is filed.")
                if (
                    "actions_summary" in vals
                    and rec.state == "closed"
                    and rec._fix_guard_differs(
                        "actions_summary", vals["actions_summary"], rec.actions_summary
                    )
                ):
                    raise UserError("%s is closed: its record of actions cannot change." % rec.name)
        return super().write(vals)

    def action_break_glass(self):
        """Open an emergency session now. Only an administrator or a Security
        Officer may; it runs for the break-glass window (4 h by default) and
        everyone who must know is told at once (AUT-SEC-10)."""
        if not _is_any(self.env, SYSTEM_GROUP, ERP_MANAGER_GROUP, OFFICER_GROUP):
            raise UserError(
                "Only an administrator or a Security Officer uses break-glass. Request the "
                "session for approval instead."
            )
        now = fields.Datetime.now().replace(microsecond=0)
        limit = min(
            _param_number(self.env, BREAK_GLASS_HOURS_PARAM, BREAK_GLASS_HOURS_DEFAULT),
            self._fix_max_hours(),
        )
        justify = _param_number(self.env, JUSTIFY_HOURS_PARAM, JUSTIFY_HOURS_DEFAULT)
        for rec in self:
            if not self.env.su and rec.user_id != self.env.user:
                raise UserError("Break-glass is used in your own name only.")
            if not rec.break_glass:
                raise UserError("%s is not an emergency break-glass request." % rec.name)
            if rec.state != "requested":
                raise UserError("%s is %s." % (rec.name, rec.state))
            hours = min(rec.duration_hours or limit, limit)
            rec.sudo()._guarded().write(
                {
                    "state": "open",
                    "started_at": now,
                    "expires_at": now + datetime.timedelta(hours=hours),
                    "justification_due_at": now + datetime.timedelta(hours=justify),
                    "decision_note": "emergency break-glass: no prior approval",
                }
            )
            self.env["fix.security.audit"].log_event(
                "privileged.break_glass_used",
                "fix.privileged.session,%d" % rec.id,
                "BREAK-GLASS %s (%s) opened by %s until %s; justification due %s"
                % (
                    rec.name,
                    rec.access_kind,
                    rec.user_id.login,
                    rec.expires_at,
                    rec.justification_due_at,
                ),
            )
            rec.sudo()._fix_notify_approvers(
                "BREAK-GLASS: %s opened emergency session %s (%s) without prior approval, "
                "until %s. Reason: %s. A written justification is due by %s."
                % (
                    rec.user_id.name,
                    rec.name,
                    rec.access_kind,
                    rec.expires_at,
                    rec.reason,
                    rec.justification_due_at,
                ),
                extra=_people(self.env, OFFICER_GROUP, SYSTEM_GROUP),
            )
        return True

    def action_close(self, summary=None):
        summary = (summary or "").strip()
        for rec in self:
            text = summary or (rec.actions_summary or "").strip()
            if len(text) < 20:
                raise UserError(
                    "Record what was done in %s before closing it (at least a sentence)." % rec.name
                )
            if summary:
                rec.sudo().write({"actions_summary": summary})
        return super().action_close()

    def action_justify(self, justification=None):
        """The holder's post-hoc justification of a break-glass session."""
        text = (justification or "").strip()
        if len(text) < 30:
            raise UserError(
                "Justify the emergency access in full (at least a couple of sentences)."
            )
        for rec in self:
            if not rec.break_glass:
                raise UserError(
                    "%s was approved in advance: it needs no post-hoc justification." % rec.name
                )
            if not self.env.su and rec.user_id != self.env.user:
                raise UserError("Only the person who used break-glass justifies it.")
            if rec.state not in ("open", "closed"):
                raise UserError("%s was never opened." % rec.name)
            if rec.reviewed_by_id:
                raise UserError("%s has been reviewed." % rec.name)
            rec.sudo()._guarded().write({"justification": text})
            self.env["fix.security.audit"].log_event(
                "privileged",
                "fix.privileged.session,%d" % rec.id,
                "break-glass %s justified by %s" % (rec.name, rec.user_id.login),
            )
        return True

    def _fix_assert_reviewer(self):
        if not _is_any(self.env, APPROVER_GROUP, OFFICER_GROUP, SYSTEM_GROUP):
            raise UserError("Only an Access Approver or a Security Officer reviews a session.")
        for rec in self:
            if not self.env.su and rec.user_id == self.env.user:
                raise UserError("Nobody reviews their own privileged session.")
            if rec.state != "closed":
                raise UserError("Review %s once it is closed." % rec.name)
            if rec.reviewed_by_id:
                raise UserError("%s is already reviewed." % rec.name)
            if rec.break_glass and not rec.justification:
                raise UserError("%s is waiting for its post-hoc justification." % rec.name)

    def action_review_ok(self):
        self._fix_assert_reviewer()
        for rec in self:
            rec.sudo()._guarded().write(
                {
                    "reviewed_by_id": self.env.uid,
                    "reviewed_on": fields.Datetime.now(),
                    "review_outcome": "justified",
                }
            )
            self.env["fix.security.audit"].log_event(
                "privileged",
                "fix.privileged.session,%d" % rec.id,
                "session %s reviewed: justified, by %s" % (rec.name, self.env.user.login),
            )
        return True

    def action_review_misuse(self, note=None):
        """Not justified: the review raises a security incident on the session."""
        note = (note or "").strip()
        if len(note) < 20:
            raise UserError("Say what was not justified (at least a sentence).")
        self._fix_assert_reviewer()
        Incident = self.env["fix.security.incident"].sudo()
        for rec in self:
            rec.sudo()._guarded().write(
                {
                    "reviewed_by_id": self.env.uid,
                    "reviewed_on": fields.Datetime.now(),
                    "review_outcome": "misuse",
                    "review_note": note[:250],
                }
            )
            incident = Incident.with_user(self.env.user).create(
                {
                    "title": "Privileged session %s not justified" % rec.name,
                    "category": "policy_breach",
                    "severity": "high",
                    "detected_by_id": self.env.uid,
                    "affected_user_id": rec.user_id.id,
                    "session_id": rec.id,
                    "description": note,
                }
            )
            self.env["fix.security.audit"].log_event(
                "privileged",
                "fix.privileged.session,%d" % rec.id,
                "session %s reviewed: NOT justified, by %s; incident %s"
                % (rec.name, self.env.user.login, incident.name),
            )
        return True

    @api.model
    def _cron_break_glass_followup(self):
        """BRU-SEC-20: a break-glass session without its justification by the due
        time is escalated once to the officers and administrators."""
        now = fields.Datetime.now()
        late = self.sudo().search(
            [
                ("break_glass", "=", True),
                ("state", "in", ("open", "closed")),
                ("justification", "=", False),
                ("justification_due_at", "<", now),
                ("justification_escalated_on", "=", False),
            ]
        )
        targets = _people(self.env, OFFICER_GROUP, SYSTEM_GROUP)
        for rec in late:
            rec._guarded().write({"justification_escalated_on": now})
            rec._fix_notify_approvers(
                "Break-glass session %s by %s has no justification (due %s): escalated."
                % (rec.name, rec.user_id.name, rec.justification_due_at),
                extra=targets,
            )
            self.env["fix.security.audit"].log_event(
                "privileged.break_glass_unjustified",
                "fix.privileged.session,%d" % rec.id,
                "break-glass %s unjustified past %s: escalated"
                % (rec.name, rec.justification_due_at),
            )
        return len(late)


# ---------------------------------------------------------------------------
# p7: penetration-test engagements tracked to closure (AUT-SEC-16, AC-26)
# ---------------------------------------------------------------------------
class FixSecurityPentest(models.Model):
    """One penetration test: who tested what and when, the report received, and
    its findings - each a vulnerability with an owner and a due date. It closes
    only when every finding is verified closed or its risk formally accepted."""

    _name = "fix.security.pentest"
    _description = "Penetration Test"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    title = fields.Char(string="Engagement", required=True)
    provider = fields.Char(string="Testing Provider", required=True)
    test_type = fields.Selection(
        [
            ("external", "External / internet-facing"),
            ("internal", "Internal network"),
            ("web_app", "Web application / API"),
            ("mobile", "Mobile application"),
            ("social", "Social engineering"),
            ("red_team", "Red team"),
        ],
        string="Test Type",
        required=True,
        default="web_app",
    )
    scope = fields.Text(required=True, help="Systems, addresses and applications in scope.")
    test_from = fields.Date(string="Testing From", required=True)
    test_to = fields.Date(string="Testing To", required=True)
    coordinator_id = fields.Many2one(
        "res.users", string="Coordinator", default=lambda self: self.env.user
    )
    report_received_on = fields.Date(string="Report Received On")
    report_ref = fields.Char(string="Report Reference", help="Document number or DMS reference.")
    finding_ids = fields.One2many("fix.vulnerability", "pentest_id", string="Findings")
    finding_count = fields.Integer(string="Findings", compute="_compute_counts")
    open_count = fields.Integer(string="Still Open", compute="_compute_counts")
    state = fields.Selection(
        [("planned", "Planned"), ("received", "Report Received"), ("closed", "Closed")],
        required=True,
        default="planned",
        tracking=True,
    )
    closed_on = fields.Datetime(readonly=True)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True)

    def _compute_counts(self):
        for rec in self:
            findings = rec.sudo().finding_ids
            rec.finding_count = len(findings)
            rec.open_count = len(findings.filtered(lambda f: f.state in ("open", "remediated")))

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "closed_on", "closed_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(rec.state == "closed" for rec in self.sudo()):
            locked |= {
                "title",
                "provider",
                "test_type",
                "scope",
                "test_from",
                "test_to",
                "coordinator_id",
                "report_received_on",
                "report_ref",
            }
        return locked

    @api.constrains("test_from", "test_to", "report_received_on")
    def _check_dates(self):
        for rec in self:
            if rec.test_to < rec.test_from:
                raise ValidationError("Testing ends on or after the day it starts.")
            if rec.report_received_on and rec.report_received_on < rec.test_from:
                raise ValidationError("The report cannot arrive before the testing started.")

    @api.model_create_multi
    def create(self, vals_list):
        self._fix_assert_officer()
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.security.pentest") or "PT/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self:
                if rec.state == "closed":
                    raise UserError("%s is closed." % rec.name)
        return super().write(vals)

    def _fix_assert_officer(self):
        if not _is_any(self.env, OFFICER_GROUP, SYSTEM_GROUP):
            raise UserError("Only a Security Officer manages penetration tests.")

    def action_receive_report(self):
        self._fix_assert_officer()
        for rec in self:
            if rec.state != "planned":
                raise UserError("%s is %s." % (rec.name, rec.state))
            if not rec.report_received_on or not (rec.report_ref or "").strip():
                raise UserError(
                    "Record the date the report arrived and its reference first (AUT-SEC-16)."
                )
            rec._guarded().write({"state": "received"})
            self.env["fix.security.audit"].log_event(
                "pentest",
                "fix.security.pentest,%d" % rec.id,
                "penetration test %s report received" % rec.name,
            )
        return True

    def action_close(self):
        """AC-26: closed only when every finding is verified or risk-accepted."""
        self._fix_assert_officer()
        for rec in self:
            if rec.state != "received":
                raise UserError("Close %s after its report is received." % rec.name)
            if rec.open_count:
                raise UserError(
                    "%s still has %d finding(s) not verified closed or risk-accepted."
                    % (rec.name, rec.open_count)
                )
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_on": fields.Datetime.now(),
                    "closed_by_id": self.env.uid,
                }
            )
            self.env["fix.security.audit"].log_event(
                "pentest",
                "fix.security.pentest,%d" % rec.id,
                "penetration test %s closed: %d finding(s) all resolved"
                % (rec.name, rec.finding_count),
            )
        return True


class FixVulnerabilityPentest(models.Model):
    _inherit = "fix.vulnerability"

    pentest_id = fields.Many2one(
        "fix.security.pentest",
        string="Penetration Test",
        index=True,
        ondelete="restrict",
        help="The engagement whose report raised this finding.",
    )

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if any(rec.state != "open" for rec in self.sudo()):
            locked.add("pentest_id")
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("pentest_id"):
                test = self.env["fix.security.pentest"].sudo().browse(vals["pentest_id"]).exists()
                if not test or test.state != "received":
                    raise UserError(
                        "Load findings into a penetration test whose report is received."
                    )
                vals["source"] = "pentest"
        return super().create(vals_list)

    def write(self, vals):
        if "pentest_id" in vals and not self._fix_guard_open():
            for rec in self.sudo():
                if rec._fix_guard_differs("pentest_id", vals["pentest_id"], rec.pentest_id):
                    if rec.state != "open":
                        raise UserError(
                            "%s is %s: the finding cannot change." % (rec.name, rec.state)
                        )
                    if rec.pentest_id:
                        raise UserError(
                            "%s already belongs to %s." % (rec.name, rec.pentest_id.name)
                        )
            if vals["pentest_id"]:
                test = self.env["fix.security.pentest"].sudo().browse(vals["pentest_id"]).exists()
                if not test or test.state != "received":
                    raise UserError(
                        "Load findings into a penetration test whose report is received."
                    )
                vals = dict(vals, source="pentest")
        return super().write(vals)
