# M30 capture audit (2026-11-14): the operational registers M30's specification
# owns (§10.1) and no code had, so the sub-module pages that cover them could
# capture nothing.
#
#   fix.scheduled.job       job registry (FR-ADM-031, BRU-ADM-11): the owner,
#                           expected duration and failure impact of a real
#                           ir.cron, plus missed-run detection (T-09)
#   fix.config.parameter    technical configuration registry (FR-ADM-013/019):
#                           the keys that may be changed through the governed
#                           path, with their type and range
#   fix.config.change       configuration change record (FR-ADM-015/018,
#                           BRU-ADM-02): proposed with an approved change
#                           reference, applied by a SECOND person, previous value
#                           kept, rolled back in one action
#   fix.backup.verification restore-test evidence (BRU-ADM-17, NFR-052)
#   fix.dr.drill            disaster-recovery drill record (BRU-ADM-18, NFR-051)
#
# Deliberately NOT built here (see the audit report): the environment ladder
# promotion, the emergency change path with auto-revert, scoped (entity/branch)
# values, change freezes, the alert and runbook registers, archive policies,
# capacity metrics, the licence register and the cost-centre hierarchy.
import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_entity import audit_event, require_platform_admin

PLATFORM_ADMIN_GROUP = "cd_entity_config.group_platform_admin"
SYSTEM_GROUP = "base.group_system"
# A key that may hold a credential never enters the registry: a change record
# keeps the previous and new value, and platform admins read change records,
# while parameter VALUES are system-only (fix_param_mask).
SECRET_HINTS = (
    "secret",
    "password",
    "passwd",
    "token",
    "api_key",
    "apikey",
    "private_key",
    "credential",
    "database.uuid",
)
KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_.\-]*$")
# NFR-007: recovery point and recovery time objectives a drill is measured against.
RPO_TARGET_MIN = 15
RTO_TARGET_MIN = 120
# T-09: a job counts as missed when its next call is this far in the past.
MISSED_GRACE_MIN = 15


def _is_platform_admin(env):
    return env.su or env.user.has_group(PLATFORM_ADMIN_GROUP) or env.user.has_group(SYSTEM_GROUP)


def _require_system(env, what):
    if env.su or env.user.has_group(SYSTEM_GROUP):
        return
    raise AccessError(
        "%s decides which technical settings the workspace may change. Only a "
        "system administrator may maintain it." % what
    )


def _changed(records, vals, keep=()):
    """The fields of `vals` that really change a value on `records`. A workspace
    form re-sends every field it shows, so an unchanged value is not an edit."""
    return {
        name
        for name in vals
        if name not in keep
        and not name.startswith("message_")
        and name in records._fields
        and any(rec._fix_guard_differs(name, vals[name], rec[name]) for rec in records)
    }


# ----------------------------------------------------------------- job registry


class FixScheduledJob(models.Model):
    _name = "fix.scheduled.job"
    _description = "Scheduled Job Registration"
    _inherit = ["mail.thread"]
    _order = "failure_impact desc, name"

    name = fields.Char(string="Job", required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    cron_id = fields.Many2one(
        "ir.cron",
        string="Scheduled Action",
        required=True,
        ondelete="cascade",
        help="The real scheduled action this registration describes.",
    )
    owning_module = fields.Char(
        string="Owning Module", help="For example M19 or cd_billing_engine."
    )
    owner_id = fields.Many2one("res.users", string="Job Owner", required=True, tracking=True)
    expected_duration_min = fields.Integer(
        string="Expected Duration (min)", required=True, default=5, tracking=True
    )
    sla_minutes = fields.Integer(
        string="SLA (min)", help="Longest acceptable run. Empty: the expected duration."
    )
    concurrent_safe = fields.Boolean(
        string="Concurrent-Safe",
        help="BRU-ADM-13: only a job declared concurrent-safe may overlap its own previous run.",
    )
    failure_impact = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        string="Failure Impact",
        required=True,
        default="medium",
        tracking=True,
    )
    failure_note = fields.Char(string="What Breaks If It Fails")
    runbook_ref = fields.Char(string="Runbook")
    active = fields.Boolean(default=True)

    # Read from the scheduled action itself, never typed.
    cron_active = fields.Boolean(string="Action Enabled", compute="_compute_cron_state")
    last_run = fields.Datetime(string="Last Run", compute="_compute_cron_state")
    next_run = fields.Datetime(string="Next Run", compute="_compute_cron_state")
    schedule = fields.Char(string="Schedule", compute="_compute_cron_state")
    run_state = fields.Selection(
        [
            ("ok", "On Schedule"),
            ("missed", "Missed Run"),
            ("never", "Never Run"),
            ("disabled", "Disabled"),
        ],
        string="Run State",
        compute="_compute_cron_state",
        help="T-09: Missed Run means the action is enabled and its next call is more than "
        "the expected duration (at least %d minutes) in the past." % MISSED_GRACE_MIN,
    )

    _cron_unique = models.Constraint(
        "UNIQUE (cron_id)", "This scheduled action is already registered."
    )

    @api.depends("cron_id", "expected_duration_min")
    def _compute_cron_state(self):
        now = fields.Datetime.now()
        for job in self:
            cron = job.cron_id.sudo()
            job.cron_active = bool(cron.active)
            job.last_run = cron.lastcall
            job.next_run = cron.nextcall
            job.schedule = (
                "every %s %s" % (cron.interval_number, cron.interval_type) if cron else False
            )
            grace = timedelta(minutes=max(MISSED_GRACE_MIN, job.expected_duration_min or 0))
            if not cron or not cron.active:
                job.run_state = "disabled"
            elif cron.nextcall and cron.nextcall < now - grace:
                job.run_state = "missed"
            elif not cron.lastcall:
                job.run_state = "never"
            else:
                job.run_state = "ok"

    @api.constrains("expected_duration_min", "sla_minutes")
    def _check_durations(self):
        for job in self:
            if job.expected_duration_min <= 0:
                raise ValidationError("The expected duration of %s must be above zero." % job.name)
            if job.sla_minutes and job.sla_minutes < job.expected_duration_min:
                raise ValidationError(
                    "The SLA of %s cannot be shorter than its expected duration." % job.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The scheduled job registry")
        for vals in vals_list:
            if not vals.get("name") and vals.get("cron_id"):
                vals["name"] = self.env["ir.cron"].sudo().browse(vals["cron_id"]).name
        jobs = super().create(vals_list)
        for job in jobs:
            audit_event(
                job.env,
                "platform.job_registered",
                "fix.scheduled.job,%d" % job.id,
                "%s, impact %s" % (job.name, job.failure_impact),
            )
        return jobs

    def write(self, vals):
        require_platform_admin(self.env, "The scheduled job registry")
        return super().write(vals)

    def unlink(self):
        require_platform_admin(self.env, "The scheduled job registry")
        return super().unlink()


# ------------------------------------------------- configuration registry


class FixConfigParameter(models.Model):
    _name = "fix.config.parameter"
    _description = "Technical Configuration Parameter"
    _inherit = ["mail.thread"]
    _rec_name = "key"
    _order = "key"

    key = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    description = fields.Char(required=True)
    value_type = fields.Selection(
        [
            ("integer", "Whole Number"),
            ("float", "Decimal"),
            ("boolean", "Yes / No"),
            ("text", "Text"),
        ],
        string="Type",
        required=True,
        default="text",
    )
    min_value = fields.Float(string="Minimum", help="Numeric types. 0 means no lower limit.")
    max_value = fields.Float(string="Maximum", help="Numeric types. 0 means no upper limit.")
    allowed_values = fields.Char(
        string="Allowed Values", help="Text only: comma-separated list of the accepted values."
    )
    default_value = fields.Char(string="Default")
    owning_module = fields.Char(string="Owning Module")
    business_impact = fields.Char(
        string="Impact If Wrong",
        required=True,
        help="BRU-ADM-23: what breaks if this is wrong. A business threshold belongs to M64.",
    )
    active = fields.Boolean(default=True)
    current_value = fields.Char(string="Current Value", compute="_compute_current_value")
    change_ids = fields.One2many("fix.config.change", "parameter_id", string="Changes")

    _key_unique = models.Constraint("UNIQUE (key)", "This key is already registered.")

    def _compute_current_value(self):
        params = self.env["ir.config_parameter"].sudo()
        for rec in self:
            rec.current_value = params.get_param(rec.key) if rec.key else False

    @api.constrains("key")
    def _check_key(self):
        for rec in self:
            key = (rec.key or "").strip()
            if not KEY_PATTERN.match(key):
                raise ValidationError(
                    "%s is not a parameter key: use lower-case letters, digits, '.', '_' "
                    "and '-'." % key
                )
            if any(hint in key for hint in SECRET_HINTS):
                raise ValidationError(
                    "%s looks like a credential. Credentials live in the vault, not in "
                    "this registry: a change record keeps the old and new value." % key
                )

    @api.constrains("value_type", "min_value", "max_value")
    def _check_range(self):
        for rec in self:
            numeric = rec.value_type in ("integer", "float")
            if numeric and rec.min_value and rec.max_value and rec.min_value > rec.max_value:
                raise ValidationError("The minimum of %s is above its maximum." % rec.key)

    def validate_value(self, raw):
        """FR-ADM-019: the value as it will be stored, or a refusal naming the rule."""
        self.ensure_one()
        value = (raw or "").strip()
        if not value:
            raise ValidationError("Give the new value of %s." % self.key)
        if self.value_type == "boolean":
            low = value.lower()
            if low not in ("true", "false", "1", "0"):
                raise ValidationError("%s takes True or False." % self.key)
            return "True" if low in ("true", "1") else "False"
        if self.value_type in ("integer", "float"):
            try:
                number = int(value) if self.value_type == "integer" else float(value)
            except ValueError as exc:
                raise ValidationError(
                    "%s takes a %s."
                    % (
                        self.key,
                        dict(self._fields["value_type"].selection)[self.value_type].lower(),
                    )
                ) from exc
            if self.min_value and number < self.min_value:
                raise ValidationError("%s cannot be below %g." % (self.key, self.min_value))
            if self.max_value and number > self.max_value:
                raise ValidationError("%s cannot be above %g." % (self.key, self.max_value))
            return str(number)
        allowed = [v.strip() for v in (self.allowed_values or "").split(",") if v.strip()]
        if allowed and value not in allowed:
            raise ValidationError("%s accepts only: %s." % (self.key, ", ".join(allowed)))
        return value

    @api.model_create_multi
    def create(self, vals_list):
        _require_system(self.env, "The configuration registry")
        for vals in vals_list:
            if vals.get("key"):
                vals["key"] = vals["key"].strip()
        return super().create(vals_list)

    def write(self, vals):
        _require_system(self.env, "The configuration registry")
        if "key" in vals and self.change_ids:
            raise UserError("A parameter that has changes on record keeps its key.")
        return super().write(vals)

    def unlink(self):
        _require_system(self.env, "The configuration registry")
        if self.change_ids:
            raise UserError("A parameter that has changes on record is archived, not deleted.")
        return super().unlink()


class FixConfigChange(models.Model):
    _name = "fix.config.change"
    _description = "Configuration Change"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    parameter_id = fields.Many2one(
        "fix.config.parameter",
        string="Parameter",
        required=True,
        ondelete="restrict",
        domain=[("active", "=", True)],
    )
    key = fields.Char(related="parameter_id.key", store=True, string="Key")
    new_value = fields.Char(string="New Value", required=True, tracking=True)
    reason = fields.Text(required=True)
    change_reference = fields.Char(
        string="Approved Change Record",
        required=True,
        help="BRU-ADM-02: the approved change (M66) this configuration change implements.",
    )
    state = fields.Selection(
        [
            ("proposed", "Proposed"),
            ("applied", "Applied"),
            ("rejected", "Rejected"),
            ("rolled_back", "Rolled Back"),
        ],
        required=True,
        default="proposed",
        tracking=True,
    )
    previous_value = fields.Char(string="Previous Value", readonly=True, copy=False)
    proposed_by_id = fields.Many2one(
        "res.users", string="Proposed By", readonly=True, default=lambda self: self.env.user
    )
    applied_by_id = fields.Many2one("res.users", string="Applied By", readonly=True, copy=False)
    applied_on = fields.Datetime(string="Applied On", readonly=True, copy=False)
    closed_by_id = fields.Many2one(
        "res.users", string="Rejected / Rolled Back By", readonly=True, copy=False
    )
    closed_on = fields.Datetime(string="Rejected / Rolled Back On", readonly=True, copy=False)
    close_reason = fields.Char(string="Rejection / Rollback Reason", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "previous_value",
            "proposed_by_id",
            "applied_by_id",
            "applied_on",
            "closed_by_id",
            "closed_on",
            "close_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "proposed":
            locked |= {"parameter_id", "new_value", "reason", "change_reference"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "A configuration change")
        Param = self.env["fix.config.parameter"]
        for vals in vals_list:
            param = Param.browse(vals.get("parameter_id")).exists()
            if not param:
                raise UserError("Choose the registered parameter to change.")
            vals["new_value"] = param.validate_value(vals.get("new_value"))
            if vals["new_value"] == (param.current_value or ""):
                raise UserError("%s already holds that value." % param.key)
            if self.search_count([("parameter_id", "=", param.id), ("state", "=", "proposed")]):
                raise UserError(
                    "%s already has a proposed change. Apply or reject it first." % param.key
                )
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.config.change") or "New"
                )
        changes = super().create(vals_list)
        for change in changes:
            change._audit("platform.config_change_proposed", "proposed")
        return changes

    def write(self, vals):
        content = {"parameter_id", "new_value", "reason", "change_reference"}
        if self and not self._fix_guard_open() and _changed(self, vals) & content:
            require_platform_admin(self.env, "A configuration change")
            for rec in self:
                if rec.state != "proposed":
                    raise UserError("%s is %s: it can no longer be edited." % (rec.name, rec.state))
            if "new_value" in vals or "parameter_id" in vals:
                for rec in self:
                    param = self.env["fix.config.parameter"].browse(
                        vals.get("parameter_id", rec.parameter_id.id)
                    )
                    value = param.validate_value(vals.get("new_value", rec.new_value))
                    super(FixConfigChange, rec).write(dict(vals, new_value=value))
                return True
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state != "proposed" and not self.env.su:
                raise UserError("%s is on record: it cannot be deleted." % rec.name)
        return super().unlink()

    def _audit(self, event, what):
        # The trail is readable by every internal user: key and change reference
        # only, never a value.
        for rec in self:
            audit_event(
                rec.env,
                event,
                "fix.config.change,%d" % rec.id,
                "%s %s %s (change %s)" % (rec.name, rec.key, what, rec.change_reference),
            )

    def _require_admin(self, what):
        if not _is_platform_admin(self.env):
            raise UserError(
                "%s needs the 'Platform Admin' role, which %s does not hold."
                % (what, self.env.user.name)
            )

    def action_apply(self):
        """BRU-ADM-02: a second platform admin applies the proposal. The value is
        validated again, the live value is kept as the previous value, and the
        setting takes effect without a restart."""
        self._require_admin("Applying a configuration change")
        params = self.env["ir.config_parameter"].sudo()
        for rec in self:
            if rec.state != "proposed":
                raise UserError(
                    "%s is %s: only a proposed change is applied." % (rec.name, rec.state)
                )
            if not rec.env.su and rec.env.user == rec.proposed_by_id:
                raise UserError(
                    "A second person applies a configuration change: you proposed %s." % rec.name
                )
            value = rec.parameter_id.validate_value(rec.new_value)
            previous = params.get_param(rec.key)
            params.set_param(rec.key, value)
            rec._guarded().write(
                {
                    "state": "applied",
                    "previous_value": previous if previous is not False else False,
                    "applied_by_id": rec.env.uid,
                    "applied_on": fields.Datetime.now(),
                }
            )
            rec._audit("platform.config_changed", "applied")
            rec.message_post(body="Applied by %s." % rec.env.user.name)
        return True

    def action_reject(self, reason=None):
        self._require_admin("Rejecting a configuration change")
        if not (reason or "").strip():
            raise UserError("Say why this change is rejected or withdrawn.")
        for rec in self:
            if rec.state != "proposed":
                raise UserError(
                    "%s is %s: only a proposed change is rejected." % (rec.name, rec.state)
                )
            rec._guarded().write(
                {
                    "state": "rejected",
                    "closed_by_id": rec.env.uid,
                    "closed_on": fields.Datetime.now(),
                    "close_reason": reason.strip(),
                }
            )
            rec._audit("platform.config_change_rejected", "rejected")
        return True

    def action_rollback(self, reason=None):
        """FR-ADM-018: one action restores the previous value. Only the latest
        applied change of a parameter rolls back, and only while the setting
        still holds the value it applied."""
        self._require_admin("Rolling back a configuration change")
        if not (reason or "").strip():
            raise UserError("Say why this change is being rolled back.")
        params = self.env["ir.config_parameter"].sudo()
        for rec in self:
            if rec.state != "applied":
                raise UserError(
                    "%s is %s: only an applied change rolls back." % (rec.name, rec.state)
                )
            later = self.search_count(
                [
                    ("parameter_id", "=", rec.parameter_id.id),
                    ("state", "=", "applied"),
                    ("id", ">", rec.id),
                ]
            )
            if later:
                raise UserError("%s has a later applied change: roll that back first." % rec.key)
            if (params.get_param(rec.key) or "") != (rec.new_value or ""):
                raise UserError(
                    "%s no longer holds the value %s applied: it was changed outside this "
                    "register. Record a new change instead." % (rec.key, rec.name)
                )
            params.set_param(rec.key, rec.previous_value or False)
            rec._guarded().write(
                {
                    "state": "rolled_back",
                    "closed_by_id": rec.env.uid,
                    "closed_on": fields.Datetime.now(),
                    "close_reason": reason.strip(),
                }
            )
            rec._audit("platform.config_rolled_back", "rolled back")
        return True


# ------------------------------------------------------------- continuity


class FixBackupVerification(models.Model):
    _name = "fix.backup.verification"
    _description = "Backup Restore Test"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "restore_tested_at desc, id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    backup_ref = fields.Char(string="Backup", required=True, help="Snapshot id or dump file.")
    backup_type = fields.Selection(
        [
            ("daily", "Daily (30 days)"),
            ("weekly", "Weekly (1 year)"),
            ("monthly", "Monthly (7 years)"),
        ],
        string="Backup Type",
        required=True,
        default="weekly",
    )
    source_environment_id = fields.Many2one(
        "fix.platform.environment", string="Backed-Up Environment"
    )
    restored_into_id = fields.Many2one("fix.platform.environment", string="Restored Into")
    taken_at = fields.Datetime(string="Backup Taken", required=True)
    restore_tested_at = fields.Datetime(
        string="Restore Tested", required=True, default=fields.Datetime.now
    )
    restore_duration_min = fields.Integer(string="Restore Duration (min)")
    result = fields.Selection(
        [("pass", "Passed"), ("fail", "Failed")], required=True, default="pass", tracking=True
    )
    evidence = fields.Char(
        required=True, help="The log, ticket or report that shows the restore and its check."
    )
    note = fields.Text()
    tested_by_id = fields.Many2one(
        "res.users", string="Tested By", readonly=True, default=lambda self: self.env.user
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"tested_by_id"}

    def _fix_form_locked_fields(self) -> set:
        # Evidence is not edited after it is filed; only the note may grow.
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= set(self._fields) - {"note", "message_ids", "message_follower_ids"}
        return locked

    @api.constrains("taken_at", "restore_tested_at", "restore_duration_min")
    def _check_times(self):
        for rec in self:
            if rec.taken_at and rec.restore_tested_at and rec.restore_tested_at < rec.taken_at:
                raise ValidationError("A backup cannot be restore-tested before it was taken.")
            if rec.restore_duration_min < 0:
                raise ValidationError("The restore duration cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The backup restore-test register")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.backup.verification") or "New"
                )
        tests = super().create(vals_list)
        for rec in tests:
            audit_event(
                rec.env,
                "platform.restore_tested",
                "fix.backup.verification,%d" % rec.id,
                "%s %s backup %s" % (rec.name, rec.backup_type, rec.result),
            )
        return tests

    def write(self, vals):
        if self and not self._fix_guard_open():
            require_platform_admin(self.env, "The backup restore-test register")
            if _changed(self, vals, keep=("note",)):
                raise UserError(
                    "A restore test is evidence: once filed only its note changes. "
                    "File a new test instead."
                )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A restore test is evidence and is never deleted.")
        return super().unlink()


class FixDrDrill(models.Model):
    _name = "fix.dr.drill"
    _description = "Disaster Recovery Drill"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "drill_date desc, id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    drill_date = fields.Date(required=True, default=fields.Date.context_today)
    scenario = fields.Selection(
        [
            ("failover", "Failover to DR"),
            ("restore", "Full restore"),
            ("tabletop", "Tabletop walk-through"),
        ],
        required=True,
        default="failover",
    )
    scope = fields.Char(required=True, help="The systems and data the drill covered.")
    environment_id = fields.Many2one("fix.platform.environment", string="DR Environment")
    rpo_achieved_min = fields.Integer(string="RPO Achieved (min)", required=True)
    rto_achieved_min = fields.Integer(string="RTO Achieved (min)", required=True)
    rpo_met = fields.Boolean(
        string="RPO Met",
        compute="_compute_met",
        store=True,
        help="NFR-007: data loss of at most %d minutes." % RPO_TARGET_MIN,
    )
    rto_met = fields.Boolean(
        string="RTO Met",
        compute="_compute_met",
        store=True,
        help="NFR-007: service back within %d minutes." % RTO_TARGET_MIN,
    )
    issues_found = fields.Text(string="Issues Found")
    actions = fields.Text(string="Follow-Up Actions")
    state = fields.Selection(
        [("recorded", "Recorded"), ("signed_off", "Signed Off")],
        required=True,
        default="recorded",
        tracking=True,
    )
    signed_off_by_id = fields.Many2one(
        "res.users", string="Signed Off By", readonly=True, copy=False
    )
    signed_off_on = fields.Datetime(string="Signed Off On", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "signed_off_by_id", "signed_off_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state == "signed_off":
            locked |= set(self._fields) - {"message_ids", "message_follower_ids"}
        return locked

    @api.depends("rpo_achieved_min", "rto_achieved_min")
    def _compute_met(self):
        for rec in self:
            rec.rpo_met = 0 <= rec.rpo_achieved_min <= RPO_TARGET_MIN
            rec.rto_met = 0 <= rec.rto_achieved_min <= RTO_TARGET_MIN

    @api.constrains("rpo_achieved_min", "rto_achieved_min")
    def _check_minutes(self):
        for rec in self:
            if rec.rpo_achieved_min < 0 or rec.rto_achieved_min < 0:
                raise ValidationError("Achieved RPO and RTO cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The DR drill register")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].sudo().next_by_code("fix.dr.drill") or "New"
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            require_platform_admin(self.env, "The DR drill register")
            if self.filtered(lambda r: r.state == "signed_off") and _changed(self, vals):
                raise UserError("A signed-off drill is frozen. Record a new drill instead.")
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda r: r.state == "signed_off") and not self.env.su:
            raise UserError("A signed-off drill is evidence and is never deleted.")
        return super().unlink()

    def action_sign_off(self):
        """BRU-ADM-18: a second platform admin signs the documented result off."""
        if not _is_platform_admin(self.env):
            raise UserError(
                "Signing off a DR drill needs the 'Platform Admin' role, which %s does "
                "not hold." % self.env.user.name
            )
        for rec in self:
            if rec.state != "recorded":
                raise UserError("%s is already signed off." % rec.name)
            if not rec.env.su and rec.env.user == rec.create_uid:
                raise UserError("A second person signs a drill off: you recorded %s." % rec.name)
            if not (rec.issues_found or "").strip() and not (rec.rpo_met and rec.rto_met):
                raise UserError(
                    "%s missed its RPO or RTO target: record the issues found before "
                    "signing it off." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "signed_off",
                    "signed_off_by_id": rec.env.uid,
                    "signed_off_on": fields.Datetime.now(),
                }
            )
            audit_event(
                rec.env,
                "platform.dr_drill_signed_off",
                "fix.dr.drill,%d" % rec.id,
                "%s %s RPO %s RTO %s"
                % (
                    rec.name,
                    rec.scenario,
                    "met" if rec.rpo_met else "missed",
                    "met" if rec.rto_met else "missed",
                ),
            )
        return True
