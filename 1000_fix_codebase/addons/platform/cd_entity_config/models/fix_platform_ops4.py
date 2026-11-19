# M30 capture audit, second pass (2026-11-19). The first pass gave every
# sub-module page a capture for each list it showed. Read against the
# specification (§5 FR-ADM, §9 BRU-ADM, §10.1), six pages still had no place
# for records the spec makes M30 own:
#
#   Branch Master     fix.branch.capability  what a branch may perform
#                                            (FR-ADM-004); the workshop refuses a
#                                            job above the branch's profile
#   Entity Structure  fix.org.change         an effective-dated, second-person
#                                            change to a branch's name, zone or
#                                            address, with the structure in force
#                                            before it kept (FR-ADM-010/011,
#                                            BRU-ADM-08)
#   Config & Flags    fix.change.freeze      freeze periods that block applying
#                                            configuration changes and turning
#                                            flags on (FR-ADM-028, BRU-ADM-22)
#                     fix.config.change      + the emergency path: applied by one
#                                            person, every Platform Admin told at
#                                            once, reverted automatically when no
#                                            change record follows within 24 h
#                                            (FR-ADM-017, BRU-ADM-04)
#                     fix.feature.flag       + owning module and planned removal
#                                            date (FR-ADM-022/027)
#                     fix.component.licence  platform component licences
#                                            (FR-ADM-021)
#   Announcements     fix.maintenance.window planned maintenance outside
#                                            08:00-23:00, at most 4 hours a month,
#                                            announced 72 hours ahead (BRU-ADM-19)
#                     fix.platform.announcement + Bengali title and message
#                                            (FR-ADM-040)
#   Audit             fix.runbook            operational runbooks (FR-ADM-038)
#                     fix.platform.alert     alerts, each with a mandatory runbook
#                                            (FR-ADM-036, BRU-ADM-14)
#                     fix.capacity.metric    the monthly capacity review
#                                            (FR-ADM-037)
#
# Still not built (see the report): archive policies and their execution, the
# job run log, environment promotion, scoped values, flag targeting by role,
# user or percentage, and single-action branch provisioning.
import math
from datetime import datetime, time, timedelta

import pytz
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_entity import audit_event, require_platform_admin
from .fix_platform_ops3 import PLATFORM_ADMIN_GROUP, _changed, _is_platform_admin

LOCAL_TZ = pytz.timezone("Asia/Dhaka")
REPAIR_LEVELS = [
    ("l1", "Level 1: Modular / Quick Fix"),
    ("l2", "Level 2: Component / Soldering"),
    ("l3", "Level 3: Chip-Level / Advanced Depot"),
]
LEVEL_ORDER = {"l1": 1, "l2": 2, "l3": 3}
# BRU-ADM-19: planned maintenance stays inside the night band and under a monthly cap.
BUSINESS_DAY_START = 8
BUSINESS_DAY_END = 23
EMERGENCY_HOURS = 24


def _require_admin_action(env, what):
    if not _is_platform_admin(env):
        raise UserError(
            "%s needs the 'Platform Admin' role, which %s does not hold." % (what, env.user.name)
        )


def _local(dt):
    """A stored (UTC, naive) datetime in Dhaka local time, naive."""
    return pytz.utc.localize(dt).astimezone(LOCAL_TZ).replace(tzinfo=None)


def _flag_changed(flags, vals, keep=()):
    """The fields of `vals` that really change a flag (fix.feature.flag has no
    guarded mixin, so this is that mixin's comparison on the flag's fields)."""
    out = set()
    for name, value in vals.items():
        if name in keep or name not in flags._fields or name.startswith("message_"):
            continue
        field = flags._fields[name]
        for flag in flags:
            try:
                new = field.convert_to_record(field.convert_to_cache(value, flag), flag)
            except Exception:
                out.add(name)
                break
            current = flag[name]
            if field.type in ("many2one", "one2many", "many2many"):
                differs = set(new.ids) != set(current.ids)
            else:
                differs = (new or False) != (current or False)
            if differs:
                out.add(name)
                break
    return out


def _sequence(env, code):
    return env["ir.sequence"].sudo().next_by_code(code) or "New"


# ------------------------------------------------------- branch capability


class FixBranchCapability(models.Model):
    _name = "fix.branch.capability"
    _description = "Branch Capability"
    _inherit = ["mail.thread"]
    _order = "branch_id, service_kind, device_category"

    branch_id = fields.Many2one(
        "fix.branch", string="Branch", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    service_kind = fields.Selection(
        [
            ("carry_in", "Carry-in repair"),
            ("onsite", "On-site / field service"),
            ("pickup", "Pickup and drop"),
            ("warranty", "Brand warranty repair"),
            ("refurbishment", "Refurbishment"),
            ("data_recovery", "Data recovery"),
            ("installation", "Installation"),
        ],
        string="Service",
        required=True,
        tracking=True,
    )
    device_category = fields.Char(
        string="Device Category", help="For example Laptop, Mobile, AC. Blank: every category."
    )
    max_repair_level = fields.Selection(
        REPAIR_LEVELS, string="Highest Repair Level", required=True, default="l1", tracking=True
    )
    effective_from = fields.Date(
        string="Effective From", required=True, default=fields.Date.context_today
    )
    note = fields.Char()
    active = fields.Boolean(default=True, tracking=True)

    # Not a SQL UNIQUE: a blank category ("every category") is NULL, and NULLs
    # never collide, so the table constraint let the same row in twice.
    @api.constrains("branch_id", "service_kind", "device_category")
    def _check_unique(self):
        for cap in self:
            category = (cap.device_category or "").strip().lower()
            twins = self.search(
                [
                    ("id", "!=", cap.id),
                    ("branch_id", "=", cap.branch_id.id),
                    ("service_kind", "=", cap.service_kind),
                ]
            ).filtered(lambda o, cat=category: (o.device_category or "").strip().lower() == cat)
            if twins:
                raise ValidationError(
                    "%s already records %s for %s: change that row instead."
                    % (
                        cap.branch_id.display_name,
                        cap.service_kind,
                        cap.device_category or "every category",
                    )
                )

    @api.depends("branch_id", "service_kind", "device_category")
    def _compute_display_name(self):
        kinds = dict(self._fields["service_kind"].selection)
        for cap in self:
            cap.display_name = "%s · %s · %s" % (
                cap.branch_id.code or "",
                kinds.get(cap.service_kind, ""),
                cap.device_category or "all categories",
            )

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The branch capability profile")
        Branch = self.env["fix.branch"]
        for vals in vals_list:
            branch = Branch.browse(vals.get("branch_id")).exists()
            if branch and not vals.get("company_id"):
                vals["company_id"] = branch.company_id.id or self.env.company.id
            if vals.get("device_category"):
                vals["device_category"] = vals["device_category"].strip() or False
        caps = super().create(vals_list)
        for cap in caps:
            audit_event(
                cap.env,
                "branch.capability_recorded",
                "fix.branch,%d" % cap.branch_id.id,
                "%s %s up to %s"
                % (cap.service_kind, cap.device_category or "all", cap.max_repair_level),
            )
        return caps

    def write(self, vals):
        require_platform_admin(self.env, "The branch capability profile")
        return super().write(vals)

    def unlink(self):
        require_platform_admin(self.env, "The branch capability profile")
        return super().unlink()


class FixBranch(models.Model):
    _inherit = "fix.branch"

    capability_ids = fields.One2many(
        "fix.branch.capability", "branch_id", string="Capability Profile"
    )

    def _fix_capability_refusal(self, repair_level, service_kind=False):
        """FR-ADM-004: why this branch may not take work at `repair_level`, or
        False. A branch with no active profile is not yet profiled and is not
        restricted: the rule starts the day its profile is recorded."""
        self.ensure_one()
        caps = (
            self.env["fix.branch.capability"]
            .sudo()
            .search([("branch_id", "=", self.id), ("active", "=", True)])
        )
        if not caps:
            return False
        if service_kind:
            caps = caps.filtered(lambda c: c.service_kind == service_kind)
            if not caps:
                return "%s does not offer %s." % (
                    self.display_name,
                    dict(self.env["fix.branch.capability"]._fields["service_kind"].selection).get(
                        service_kind, service_kind
                    ),
                )
        best = max(LEVEL_ORDER.get(c.max_repair_level, 0) for c in caps)
        if LEVEL_ORDER.get(repair_level, 0) > best:
            return (
                "%s is profiled for repairs up to level %d. A level %d repair goes to a "
                "branch or depot that can perform it."
                % (self.display_name, best, LEVEL_ORDER.get(repair_level, 0))
            )
        return False


# ------------------------------------------------------ organisation change


class FixOrgChange(models.Model):
    _name = "fix.org.change"
    _description = "Organisation Change"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "effective_from desc, id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    branch_id = fields.Many2one(
        "fix.branch", string="Branch", required=True, ondelete="restrict", index=True
    )
    change_type = fields.Selection(
        [
            ("rename", "Rename"),
            ("zone_move", "Move to another zone"),
            ("relocation", "Relocation (new address)"),
        ],
        string="Change",
        required=True,
        default="rename",
    )
    new_name = fields.Char(string="New Name")
    new_name_bn = fields.Char(string="New Name (Bengali)")
    new_zone_id = fields.Many2one("fix.zone", string="New Zone")
    new_address_id = fields.Many2one("fix.bd.address", string="New Address")
    effective_from = fields.Date(
        string="Effective From", required=True, default=fields.Date.context_today
    )
    reason = fields.Text(required=True)
    state = fields.Selection(
        [
            ("proposed", "Proposed"),
            ("approved", "Approved (awaiting date)"),
            ("applied", "In Force"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="proposed",
        tracking=True,
    )
    previous_state = fields.Char(string="Structure Before", readonly=True, copy=False)
    new_state = fields.Char(string="Structure After", compute="_compute_new_state")
    proposed_by_id = fields.Many2one(
        "res.users", string="Proposed By", readonly=True, default=lambda self: self.env.user
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_on = fields.Datetime(string="Approved On", readonly=True, copy=False)
    applied_on = fields.Datetime(string="In Force Since", readonly=True, copy=False)
    reject_reason = fields.Char(string="Rejection Reason", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "previous_state",
            "proposed_by_id",
            "approved_by_id",
            "approved_on",
            "applied_on",
            "reject_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "proposed":
            locked |= set(self._fields) - {"message_ids", "message_follower_ids"}
        return locked

    @api.depends("change_type", "new_name", "new_name_bn", "new_zone_id", "new_address_id")
    def _compute_new_state(self):
        for rec in self:
            rec.new_state = rec._describe_target()

    def _describe_target(self):
        if self.change_type == "rename":
            return "Name: %s" % (self.new_name or "-")
        if self.change_type == "zone_move":
            return "Zone: %s" % (self.new_zone_id.display_name or "-")
        return "Address: %s" % (self.new_address_id.display_name or "-")

    def _describe_current(self):
        branch = self.branch_id
        if self.change_type == "rename":
            return "Name: %s" % branch.name
        if self.change_type == "zone_move":
            return "Zone: %s" % (branch.zone_id.display_name or "none")
        return "Address: %s" % (branch.address_id.display_name or "none")

    @api.constrains("change_type", "new_name", "new_zone_id", "new_address_id", "branch_id")
    def _check_target(self):
        for rec in self:
            branch = rec.branch_id
            if rec.change_type == "rename":
                if not (rec.new_name or "").strip():
                    raise ValidationError("Give the branch's new name.")
                if rec.state == "proposed" and rec.new_name.strip() == branch.name:
                    raise ValidationError("%s already has that name." % branch.display_name)
            elif rec.change_type == "zone_move":
                if not rec.new_zone_id:
                    raise ValidationError("Choose the zone the branch moves to.")
                if rec.state == "proposed" and rec.new_zone_id == branch.zone_id:
                    raise ValidationError("%s is already in that zone." % branch.display_name)
            elif not rec.new_address_id:
                raise ValidationError("Choose the branch's new address.")

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "An organisation change")
        today = fields.Date.context_today(self)
        Branch = self.env["fix.branch"]
        for vals in vals_list:
            when = fields.Date.to_date(vals.get("effective_from")) or today
            if when < today:
                raise UserError(
                    "An organisation change takes effect from today or later (BRU-ADM-08): "
                    "history is never rewritten backwards."
                )
            branch = Branch.browse(vals.get("branch_id")).exists()
            if branch and not vals.get("company_id"):
                vals["company_id"] = branch.company_id.id or self.env.company.id
            if vals.get("name", "New") == "New":
                vals["name"] = _sequence(self.env, "fix.org.change")
        changes = super().create(vals_list)
        for rec in changes:
            open_same = self.search_count(
                [
                    ("branch_id", "=", rec.branch_id.id),
                    ("change_type", "=", rec.change_type),
                    ("state", "in", ("proposed", "approved")),
                    ("id", "!=", rec.id),
                ]
            )
            if open_same:
                raise UserError(
                    "%s already has an open %s change. Decide that one first."
                    % (rec.branch_id.display_name, rec.change_type.replace("_", " "))
                )
            rec._audit("org.change_proposed")
        return changes

    def write(self, vals):
        if self and not self._fix_guard_open() and _changed(self, vals):
            require_platform_admin(self.env, "An organisation change")
            for rec in self:
                if rec.state != "proposed":
                    raise UserError("%s is %s: it can no longer be edited." % (rec.name, rec.state))
            if "effective_from" in vals:
                when = fields.Date.to_date(vals["effective_from"])
                if when and when < fields.Date.context_today(self):
                    raise UserError("An organisation change takes effect from today or later.")
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state != "proposed" and not self.env.su:
                raise UserError("%s is part of the structure history and is kept." % rec.name)
        return super().unlink()

    def _audit(self, event):
        for rec in self:
            audit_event(
                rec.env,
                event,
                "fix.org.change,%d" % rec.id,
                "%s %s %s from %s"
                % (rec.name, rec.branch_id.code, rec.change_type, rec.effective_from),
            )

    def action_approve(self):
        """A second Platform Admin approves. A change effective today applies at
        once; a later one waits for its date (the daily job applies it)."""
        _require_admin_action(self.env, "Approving an organisation change")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "proposed":
                raise UserError(
                    "%s is %s: only a proposed change is approved." % (rec.name, rec.state)
                )
            if not rec.env.su and rec.env.user == rec.proposed_by_id:
                raise UserError("A second person approves: you proposed %s." % rec.name)
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": rec.env.uid,
                    "approved_on": fields.Datetime.now(),
                }
            )
            rec._audit("org.change_approved")
            if rec.effective_from <= today:
                rec._apply()
        return True

    def action_reject(self, reason=None):
        _require_admin_action(self.env, "Rejecting an organisation change")
        if not (reason or "").strip():
            raise UserError("Say why this change is rejected or withdrawn.")
        for rec in self:
            if rec.state not in ("proposed", "approved"):
                raise UserError("%s is %s: it can no longer be rejected." % (rec.name, rec.state))
            rec._guarded().write({"state": "rejected", "reject_reason": reason.strip()})
            rec._audit("org.change_rejected")
        return True

    def _apply(self):
        for rec in self:
            branch = rec.branch_id.sudo()
            before = rec._describe_current()
            if rec.change_type == "rename":
                vals = {"name": rec.new_name.strip()}
                if rec.new_name_bn:
                    vals["name_bn"] = rec.new_name_bn.strip()
            elif rec.change_type == "zone_move":
                vals = {"zone_id": rec.new_zone_id.id}
            else:
                vals = {"address_id": rec.new_address_id.id}
            branch.write(vals)
            branch.message_post(
                body="%s in force from %s: %s -> %s (approved by %s)."
                % (
                    rec.name,
                    rec.effective_from,
                    before,
                    rec._describe_target(),
                    rec.approved_by_id.name,
                )
            )
            rec._guarded().write(
                {"state": "applied", "previous_state": before, "applied_on": fields.Datetime.now()}
            )
            rec._audit("org.change_applied")

    @api.model
    def cron_apply_due_changes(self):
        due = self.sudo().search(
            [("state", "=", "approved"), ("effective_from", "<=", fields.Date.context_today(self))]
        )
        due._apply()
        return len(due)


# ----------------------------------------------------------- change freeze


class FixChangeFreeze(models.Model):
    _name = "fix.change.freeze"
    _description = "Change Freeze"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "date_from desc"

    name = fields.Char(required=True, tracking=True, help="For example: Eid sales freeze.")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    date_from = fields.Datetime(string="Freeze Starts", required=True, tracking=True)
    date_to = fields.Datetime(string="Freeze Ends", required=True, tracking=True)
    scope = fields.Selection(
        [
            ("all", "Configuration changes and feature flags"),
            ("config", "Configuration changes only"),
            ("flags", "Feature flags only"),
        ],
        required=True,
        default="all",
        tracking=True,
    )
    reason = fields.Text(required=True)
    declared_by_id = fields.Many2one(
        "res.users", string="Declared By", readonly=True, default=lambda self: self.env.user
    )
    lifted_by_id = fields.Many2one("res.users", string="Lifted Early By", readonly=True, copy=False)
    lift_reason = fields.Char(string="Lift Reason", readonly=True, copy=False)
    status = fields.Selection(
        [("scheduled", "Scheduled"), ("active", "In Force"), ("ended", "Ended")],
        compute="_compute_status",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"declared_by_id", "lifted_by_id", "lift_reason"}

    @api.depends("date_from", "date_to")
    def _compute_status(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.date_to and rec.date_to <= now:
                rec.status = "ended"
            elif rec.date_from and rec.date_from <= now:
                rec.status = "active"
            else:
                rec.status = "scheduled"

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to <= rec.date_from:
                raise ValidationError("A freeze ends after it starts.")

    @api.model
    def active_freeze(self, scope):
        """BRU-ADM-22: the freeze in force now that covers `scope` (config or
        flags), read as the server so no caller can dodge it."""
        now = fields.Datetime.now()
        return self.sudo().search(
            [
                ("date_from", "<=", now),
                ("date_to", ">", now),
                ("scope", "in", ("all", scope)),
                ("company_id", "in", [*self.env.companies.ids, False]),
            ],
            limit=1,
        )

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "A change freeze")
        freezes = super().create(vals_list)
        for rec in freezes:
            audit_event(
                rec.env,
                "platform.freeze_declared",
                "fix.change.freeze,%d" % rec.id,
                "%s %s to %s (%s)" % (rec.name, rec.date_from, rec.date_to, rec.scope),
            )
        return freezes

    def write(self, vals):
        if self and not self._fix_guard_open() and _changed(self, vals):
            require_platform_admin(self.env, "A change freeze")
            started = self.filtered(lambda r: r.status != "scheduled")
            if started:
                raise UserError(
                    "%s has started: it can only be lifted early, with a reason."
                    % ", ".join(started.mapped("name"))
                )
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda r: r.status != "scheduled") and not self.env.su:
            raise UserError("A freeze that has started is on record and is not deleted.")
        require_platform_admin(self.env, "A change freeze")
        return super().unlink()

    def action_lift(self, reason=None):
        _require_admin_action(self.env, "Lifting a change freeze")
        if not (reason or "").strip():
            raise UserError("Say why the freeze is lifted early.")
        now = fields.Datetime.now()
        for rec in self:
            if rec.status != "active":
                raise UserError("%s is not in force." % rec.name)
            rec._guarded().write(
                {"date_to": now, "lifted_by_id": rec.env.uid, "lift_reason": reason.strip()}
            )
            audit_event(
                rec.env,
                "platform.freeze_lifted",
                "fix.change.freeze,%d" % rec.id,
                "%s lifted early" % rec.name,
            )
        return True


def _refuse_if_frozen(env, scope, what):
    freeze = env["fix.change.freeze"].active_freeze(scope)
    if freeze:
        raise UserError(
            "%s is blocked: the change freeze '%s' is in force until %s (BRU-ADM-22). "
            "Use the emergency path for a change that cannot wait."
            % (what, freeze.name, fields.Datetime.to_string(freeze.date_to))
        )


# ------------------------------------------ emergency configuration change


class FixConfigChange(models.Model):
    _inherit = "fix.config.change"

    # A routine change cites its approved change record up front; an emergency
    # change files it within 24 hours or is reverted (BRU-ADM-04).
    change_reference = fields.Char(required=False)
    emergency = fields.Boolean(
        string="Emergency Change",
        help="FR-ADM-017: applied at once by one Platform Admin, every Platform Admin is "
        "told, and the approved change record must follow within 24 hours or the change "
        "is reverted automatically.",
    )
    regularise_by = fields.Datetime(string="Change Record Due By", readonly=True, copy=False)
    regularised_on = fields.Datetime(string="Change Record Filed On", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"regularise_by", "regularised_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "proposed":
            locked |= {"emergency"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("emergency") and not (vals.get("change_reference") or "").strip():
                raise UserError(
                    "Cite the approved change record (M66) this change implements "
                    "(BRU-ADM-02). Only an emergency change files it afterwards."
                )
        return super().create(vals_list)

    def write(self, vals):
        if (
            self
            and not self._fix_guard_open()
            and "change_reference" in vals
            and not (vals["change_reference"] or "").strip()
            and self.filtered(lambda r: not r.emergency)
        ):
            raise UserError("A routine configuration change keeps its change record.")
        return super().write(vals)

    def action_apply(self):
        if self.filtered("emergency"):
            raise UserError(
                "An emergency change is applied with 'Apply as Emergency', which tells every "
                "Platform Admin at once."
            )
        _refuse_if_frozen(self.env, "config", "Applying a configuration change")
        return super().action_apply()

    def action_apply_emergency(self):
        """FR-ADM-017 / BRU-ADM-04: the proposer applies alone, the change is
        loud (every Platform Admin is notified now) and time-boxed (no change
        record within 24 hours means the cron reverts it). A freeze does not
        block it: that is what the path is for."""
        _require_admin_action(self.env, "Applying an emergency configuration change")
        params = self.env["ir.config_parameter"].sudo()
        admins = self.env.ref(PLATFORM_ADMIN_GROUP).sudo().user_ids
        for rec in self:
            if not rec.emergency:
                raise UserError(
                    "%s is not an emergency change: a second person applies it." % rec.name
                )
            if rec.state != "proposed":
                raise UserError(
                    "%s is %s: only a proposed change is applied." % (rec.name, rec.state)
                )
            value = rec.parameter_id.validate_value(rec.new_value)
            previous = params.get_param(rec.key)
            params.set_param(rec.key, value)
            now = fields.Datetime.now()
            rec._guarded().write(
                {
                    "state": "applied",
                    "previous_value": previous if previous is not False else False,
                    "applied_by_id": rec.env.uid,
                    "applied_on": now,
                    "regularise_by": False
                    if (rec.change_reference or "").strip()
                    else now + timedelta(hours=EMERGENCY_HOURS),
                    "regularised_on": now if (rec.change_reference or "").strip() else False,
                }
            )
            rec._audit("platform.config_emergency_applied", "applied as an emergency")
            rec.sudo().message_post(
                body="EMERGENCY configuration change %s applied by %s to %s. %s"
                % (
                    rec.name,
                    rec.env.user.name,
                    rec.key,
                    "A change record is on file."
                    if (rec.change_reference or "").strip()
                    else "File the approved change record within %d hours or it is reverted "
                    "automatically." % EMERGENCY_HOURS,
                ),
                partner_ids=(admins - rec.env.user).partner_id.ids,
                subtype_xmlid="mail.mt_comment",
            )
        return True

    def action_regularise(self, reference=None):
        """The retrospective change record of an emergency change."""
        _require_admin_action(self.env, "Filing the change record of an emergency change")
        if not (reference or "").strip():
            raise UserError("Give the approved change record (M66) for this emergency change.")
        for rec in self:
            if not rec.emergency or rec.state != "applied" or rec.regularised_on:
                raise UserError("%s is not an emergency change awaiting its record." % rec.name)
            rec._guarded().write(
                {
                    "change_reference": reference.strip(),
                    "regularised_on": fields.Datetime.now(),
                    "regularise_by": False,
                }
            )
            rec._audit("platform.config_emergency_regularised", "regularised")
        return True

    @api.model
    def cron_revert_unregularised(self):
        """BRU-ADM-04: an emergency change with no change record by its deadline
        is reverted, unless the setting was changed again since (then it is left
        and the reversion is refused on the record for a person to decide)."""
        params = self.env["ir.config_parameter"].sudo()
        overdue = self.sudo().search(
            [
                ("emergency", "=", True),
                ("state", "=", "applied"),
                ("regularised_on", "=", False),
                ("regularise_by", "<", fields.Datetime.now()),
            ]
        )
        reverted = self.browse()
        for rec in overdue:
            if (params.get_param(rec.key) or "") != (rec.new_value or ""):
                rec.message_post(
                    body="Not reverted: %s was changed again after this emergency change. "
                    "A Platform Admin must decide." % rec.key
                )
                rec._guarded().write({"regularise_by": False})
                continue
            params.set_param(rec.key, rec.previous_value or False)
            rec._guarded().write(
                {
                    "state": "rolled_back",
                    "closed_on": fields.Datetime.now(),
                    "close_reason": "Reverted automatically: no change record within %d hours "
                    "(BRU-ADM-04)." % EMERGENCY_HOURS,
                }
            )
            rec._audit("platform.config_emergency_reverted", "reverted automatically")
            reverted |= rec
        return reverted


# ---------------------------------------------------------- feature flags


class FixFeatureFlag(models.Model):
    _inherit = "fix.feature.flag"

    owning_module = fields.Char(string="Owning Module", help="For example M02.")
    planned_removal_date = fields.Date(
        string="Planned Removal",
        help="FR-ADM-022/027: when the flag is due to be removed once the capability is "
        "permanent. A flag past this date is reported as stale.",
    )
    stale = fields.Boolean(string="Past Removal Date", compute="_compute_stale")

    def _compute_stale(self):
        today = fields.Date.context_today(self)
        for flag in self:
            flag.stale = bool(flag.planned_removal_date and flag.planned_removal_date < today)

    def write(self, vals):
        # BRU-ADM-22: during a freeze a flag may still be switched OFF (the kill
        # switch is an emergency tool, OPS-06); nothing else about it changes.
        if self and not self.env.su:
            changed = _flag_changed(self, vals, keep=("owning_module", "planned_removal_date"))
            kill_only = changed <= {"enabled"} and not vals.get("enabled")
            if changed and not kill_only:
                _refuse_if_frozen(self.env, "flags", "Changing a feature flag")
        return super().write(vals)


# ------------------------------------------------------- licence register


class FixComponentLicence(models.Model):
    _name = "fix.component.licence"
    _description = "Platform Component Licence"
    _inherit = ["mail.thread"]
    _order = "component, version"

    component = fields.Char(required=True, tracking=True)
    version = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    licence = fields.Char(string="Licence (SPDX)", required=True, help="For example LGPL-3.0, MIT.")
    licence_class = fields.Selection(
        [
            ("permissive", "Permissive"),
            ("weak_copyleft", "Weak copyleft"),
            ("strong_copyleft", "Strong copyleft"),
            ("network_copyleft", "Network copyleft (AGPL)"),
            ("source_available", "Source-available (BSL, SSPL, fair-code)"),
            ("commercial", "Commercial"),
        ],
        string="Class",
        required=True,
        default="permissive",
        tracking=True,
    )
    obligation_summary = fields.Text(string="Obligations")
    compliance_note = fields.Text(
        string="How We Comply",
        help="Required for copyleft, source-available and commercial components.",
    )
    owner_id = fields.Many2one("res.users", string="Owner", default=lambda self: self.env.user)
    reviewed_on = fields.Date(string="Last Reviewed", default=fields.Date.context_today)
    next_review_due = fields.Date(string="Next Review Due", required=True)
    review_overdue = fields.Boolean(string="Review Overdue", compute="_compute_overdue")
    active = fields.Boolean(default=True)

    _component_version_unique = models.Constraint(
        "UNIQUE (component, version)", "This component version is already registered."
    )

    @api.depends("next_review_due")
    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.review_overdue = bool(rec.next_review_due and rec.next_review_due < today)

    @api.constrains("licence_class", "compliance_note", "reviewed_on", "next_review_due")
    def _check_compliance(self):
        for rec in self:
            if rec.licence_class != "permissive" and not (rec.compliance_note or "").strip():
                raise ValidationError(
                    "%s %s is %s: say how we meet its obligations."
                    % (
                        rec.component,
                        rec.version,
                        dict(self._fields["licence_class"].selection)[rec.licence_class].lower(),
                    )
                )
            if rec.reviewed_on and rec.next_review_due and rec.next_review_due < rec.reviewed_on:
                raise ValidationError("The next review falls after the last one.")

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The component licence register")
        return super().create(vals_list)

    def write(self, vals):
        require_platform_admin(self.env, "The component licence register")
        return super().write(vals)

    def unlink(self):
        require_platform_admin(self.env, "The component licence register")
        return super().unlink()


# ---------------------------------------------------- maintenance windows


class FixMaintenanceWindow(models.Model):
    _name = "fix.maintenance.window"
    _description = "Planned Maintenance Window"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "scheduled_from desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    scheduled_from = fields.Datetime(string="Starts", required=True, tracking=True)
    scheduled_to = fields.Datetime(string="Ends", required=True, tracking=True)
    planned_minutes = fields.Integer(string="Planned (min)", compute="_compute_minutes", store=True)
    scope = fields.Char(required=True, help="What is taken down or changed.")
    impact = fields.Selection(
        [
            ("none", "No user impact"),
            ("degraded", "Degraded service"),
            ("outage", "Service unavailable"),
        ],
        required=True,
        default="outage",
    )
    environment_id = fields.Many2one("fix.platform.environment", string="Environment")
    announcement_id = fields.Many2one(
        "fix.platform.announcement", string="Announcement", readonly=True, copy=False
    )
    announcement_state = fields.Selection(
        related="announcement_id.state", string="Announcement Status"
    )
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="planned",
        tracking=True,
    )
    actual_from = fields.Datetime(string="Actually Started", readonly=True, copy=False)
    actual_to = fields.Datetime(string="Actually Ended", readonly=True, copy=False)
    overran = fields.Boolean(compute="_compute_minutes", store=True)
    outcome_note = fields.Text(string="Outcome")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "announcement_id",
            "actual_from",
            "actual_to",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and (self.announcement_id or self.state != "planned"):
            locked |= {"scheduled_from", "scheduled_to", "scope", "impact", "environment_id"}
        return locked

    @api.depends("scheduled_from", "scheduled_to", "actual_to")
    def _compute_minutes(self):
        for rec in self:
            if rec.scheduled_from and rec.scheduled_to:
                rec.planned_minutes = int(
                    (rec.scheduled_to - rec.scheduled_from).total_seconds() // 60
                )
            else:
                rec.planned_minutes = 0
            rec.overran = bool(
                rec.actual_to and rec.scheduled_to and rec.actual_to > rec.scheduled_to
            )

    @api.model
    def _monthly_cap(self):
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("fix_maintenance.monthly_cap_minutes", "240")
        )

    @api.constrains("scheduled_from", "scheduled_to", "state")
    def _check_window(self):
        """BRU-ADM-19: outside 08:00-23:00 Dhaka time and at most the monthly cap."""
        for rec in self:
            if rec.state == "cancelled" or not (rec.scheduled_from and rec.scheduled_to):
                continue
            if rec.scheduled_to <= rec.scheduled_from:
                raise ValidationError("A maintenance window ends after it starts.")
            start, end = _local(rec.scheduled_from), _local(rec.scheduled_to)
            if start.hour >= BUSINESS_DAY_END:
                night_end = datetime.combine(
                    start.date() + timedelta(days=1), time(BUSINESS_DAY_START)
                )
            elif start.hour < BUSINESS_DAY_START:
                night_end = datetime.combine(start.date(), time(BUSINESS_DAY_START))
            else:
                night_end = None
            if night_end is None or end > night_end:
                raise ValidationError(
                    "Planned maintenance runs between 23:00 and 08:00 Dhaka time (BRU-ADM-19): "
                    "%s to %s crosses business hours."
                    % (start.strftime("%d %b %H:%M"), end.strftime("%d %b %H:%M"))
                )
            month_start = datetime(start.year, start.month, 1)
            month_end = month_start + relativedelta(months=1)
            others = self.search(
                [
                    ("id", "!=", rec.id),
                    ("state", "!=", "cancelled"),
                    ("company_id", "=", rec.company_id.id),
                ]
            )
            others = others.filtered(
                lambda w, lo=month_start, hi=month_end: lo <= _local(w.scheduled_from) < hi
            )
            used = sum(others.mapped("planned_minutes")) + rec.planned_minutes
            cap = rec._monthly_cap()
            if used > cap:
                raise ValidationError(
                    "Planned maintenance is capped at %d minutes a month (BRU-ADM-19): %s would "
                    "bring %s to %d minutes." % (cap, rec.name, start.strftime("%B %Y"), used)
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "A maintenance window")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _sequence(self.env, "fix.maintenance.window")
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open() and _changed(self, vals):
            require_platform_admin(self.env, "A maintenance window")
            done = self.filtered(lambda r: r.state in ("completed", "cancelled"))
            if done and _changed(done, vals, keep=("outcome_note",)):
                raise UserError("A completed or cancelled window keeps its record.")
            fixed = {"scheduled_from", "scheduled_to"}
            if self.filtered("announcement_id") and _changed(self, vals) & fixed:
                raise UserError(
                    "The window has been announced: cancel it and plan a new one rather than "
                    "move it under the announcement."
                )
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda r: r.state != "planned" or r.announcement_id) and not self.env.su:
            raise UserError("An announced or started window is on record: cancel it instead.")
        return super().unlink()

    def action_raise_announcement(self):
        """Drafts the planned-maintenance announcement. A second Platform Admin
        publishes it, and publishing refuses less than 72 hours of lead."""
        _require_admin_action(self.env, "Announcing a maintenance window")
        Announcement = self.env["fix.platform.announcement"]
        for rec in self:
            if rec.state != "planned":
                raise UserError("%s is %s." % (rec.name, rec.state))
            if rec.announcement_id:
                raise UserError("%s already has its announcement." % rec.name)
            start, end = _local(rec.scheduled_from), _local(rec.scheduled_to)
            impact = dict(self._fields["impact"].selection)[rec.impact]
            announcement = Announcement.create(
                {
                    "name": "Planned maintenance %s" % start.strftime("%d %b %Y"),
                    "kind": "maintenance",
                    "severity": "warning" if rec.impact != "none" else "info",
                    "audience": "all",
                    "maintenance_start": rec.scheduled_from,
                    "publish_on": fields.Date.context_today(self),
                    "expires_on": end.date(),
                    "body": "%s, %s to %s (Dhaka time). %s: %s."
                    % (
                        rec.name,
                        start.strftime("%d %b %H:%M"),
                        end.strftime("%H:%M"),
                        impact,
                        rec.scope,
                    ),
                }
            )
            rec._guarded().write({"announcement_id": announcement.id})
        return True

    def action_start(self):
        _require_admin_action(self.env, "Starting maintenance")
        for rec in self:
            if rec.state != "planned":
                raise UserError("%s is %s." % (rec.name, rec.state))
            if rec.announcement_state not in ("published", "retired"):
                raise UserError(
                    "%s was not announced: its announcement must be published 72 hours ahead "
                    "(BRU-ADM-19) before the work starts." % rec.name
                )
            rec._guarded().write({"state": "in_progress", "actual_from": fields.Datetime.now()})
        return True

    def action_complete(self):
        _require_admin_action(self.env, "Completing maintenance")
        for rec in self:
            if rec.state != "in_progress":
                raise UserError("%s has not started." % rec.name)
            rec._guarded().write({"state": "completed", "actual_to": fields.Datetime.now()})
            audit_event(
                rec.env,
                "platform.maintenance_completed",
                "fix.maintenance.window,%d" % rec.id,
                "%s %s" % (rec.name, "overran" if rec.overran else "on time"),
            )
        return True

    def action_cancel(self, reason=None):
        _require_admin_action(self.env, "Cancelling maintenance")
        if not (reason or "").strip():
            raise UserError("Say why the maintenance is cancelled.")
        for rec in self:
            if rec.state not in ("planned",):
                raise UserError("%s is %s: it cannot be cancelled." % (rec.name, rec.state))
            if rec.announcement_id and rec.announcement_id.state != "retired":
                rec.announcement_id.action_retire()
            rec._guarded().write({"state": "cancelled", "outcome_note": reason.strip()})
        return True


class FixPlatformAnnouncement(models.Model):
    _inherit = "fix.platform.announcement"

    # FR-ADM-040: announcements are published in Bengali and English.
    name_bn = fields.Char(string="Title (Bengali)")
    body_bn = fields.Text(string="Message (Bengali)")


# ------------------------------------------------- runbooks and alerts


class FixRunbook(models.Model):
    _name = "fix.runbook"
    _description = "Operational Runbook"
    _inherit = ["mail.thread"]
    _order = "scope, code"

    code = fields.Char(required=True, tracking=True)
    name = fields.Char(string="Title", required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    scope = fields.Selection(
        [
            ("module", "Module"),
            ("alert", "Alert"),
            ("job", "Scheduled job"),
            ("procedure", "Procedure"),
        ],
        required=True,
        default="procedure",
    )
    reference = fields.Char(
        string="Covers", help="The module (M30), job or procedure this runbook covers."
    )
    document_url = fields.Char(string="Document Link")
    steps = fields.Text(string="Steps")
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )
    last_reviewed_on = fields.Date(
        string="Last Reviewed", default=fields.Date.context_today, tracking=True
    )
    review_months = fields.Integer(string="Review Every (months)", required=True, default=12)
    next_review_due = fields.Date(
        string="Next Review Due", compute="_compute_next_review", store=True
    )
    review_overdue = fields.Boolean(string="Review Overdue", compute="_compute_overdue")
    alert_ids = fields.One2many("fix.platform.alert", "runbook_id", string="Alerts")
    active = fields.Boolean(default=True, tracking=True)

    _code_unique = models.Constraint("UNIQUE (code)", "This runbook code is already used.")

    @api.depends("last_reviewed_on", "review_months")
    def _compute_next_review(self):
        for rec in self:
            rec.next_review_due = (
                rec.last_reviewed_on + relativedelta(months=rec.review_months or 12)
                if rec.last_reviewed_on
                else False
            )

    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.review_overdue = not rec.next_review_due or rec.next_review_due < today

    @api.constrains("document_url", "steps", "review_months")
    def _check_content(self):
        for rec in self:
            if not (rec.document_url or "").strip() and not (rec.steps or "").strip():
                raise ValidationError(
                    "Runbook %s needs its steps or a link to the document that holds them."
                    % rec.code
                )
            if rec.review_months <= 0:
                raise ValidationError("A runbook is reviewed at least once a period.")

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The runbook register")
        return super().create(vals_list)

    def write(self, vals):
        require_platform_admin(self.env, "The runbook register")
        if vals.get("active") is False and not self.env.su:
            used = self.env["fix.platform.alert"].search_count(
                [("runbook_id", "in", self.ids), ("active", "=", True)]
            )
            if used:
                raise UserError(
                    "An active alert relies on this runbook (BRU-ADM-14). Point the alert at "
                    "another runbook or retire it first."
                )
        return super().write(vals)

    def unlink(self):
        require_platform_admin(self.env, "The runbook register")
        if self.alert_ids and not self.env.su:
            raise UserError("A runbook that alerts point to is archived, not deleted.")
        return super().unlink()

    def action_mark_reviewed(self):
        _require_admin_action(self.env, "Recording a runbook review")
        today = fields.Date.context_today(self)
        for rec in self:
            rec.write({"last_reviewed_on": today})
            rec.message_post(body="Reviewed by %s." % rec.env.user.name)
        return True


class FixPlatformAlert(models.Model):
    _name = "fix.platform.alert"
    _description = "Platform Alert"
    _inherit = ["mail.thread"]
    _order = "severity, code"

    code = fields.Char(required=True, tracking=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    source = fields.Selection(
        [
            ("application", "Application"),
            ("database", "Database"),
            ("job", "Scheduled job"),
            ("queue", "Queue / worker"),
            ("integration", "Integration (M28)"),
            ("security", "Security (M29)"),
            ("capacity", "Capacity"),
            ("backup", "Backup"),
        ],
        required=True,
        default="application",
    )
    severity = fields.Selection(
        [("p1", "P1 Critical"), ("p2", "P2 High"), ("p3", "P3 Medium"), ("p4", "P4 Low")],
        required=True,
        default="p3",
        tracking=True,
    )
    threshold_expression = fields.Char(
        string="Fires When", required=True, help="For example: queue depth > 500 for 10 min."
    )
    routing = fields.Char(
        string="Routed To", required=True, help="Who is paged, and how (on-call rota, channel)."
    )
    runbook_id = fields.Many2one(
        "fix.runbook",
        string="Runbook",
        required=True,
        ondelete="restrict",
        help="BRU-ADM-14: an alert without an action is noise and is removed.",
    )
    active = fields.Boolean(default=True, tracking=True)

    _code_unique = models.Constraint("UNIQUE (code)", "This alert code is already used.")

    @api.constrains("runbook_id", "active")
    def _check_runbook(self):
        for rec in self:
            if rec.active and not rec.runbook_id.active:
                raise ValidationError(
                    "Alert %s points to an archived runbook: every alert has a live runbook "
                    "(BRU-ADM-14)." % rec.code
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The alert register")
        return super().create(vals_list)

    def write(self, vals):
        require_platform_admin(self.env, "The alert register")
        return super().write(vals)

    def unlink(self):
        require_platform_admin(self.env, "The alert register")
        return super().unlink()


class FixScheduledJob(models.Model):
    _inherit = "fix.scheduled.job"

    runbook_id = fields.Many2one("fix.runbook", string="Runbook Record", ondelete="set null")


# --------------------------------------------------------- capacity review


class FixCapacityMetric(models.Model):
    _name = "fix.capacity.metric"
    _description = "Capacity Review"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "measured_on desc, resource"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    resource = fields.Char(required=True, help="For example: PostgreSQL data volume.")
    dimension = fields.Selection(
        [
            ("storage_gb", "Storage (GB)"),
            ("cpu_pct", "CPU (%)"),
            ("memory_gb", "Memory (GB)"),
            ("db_connections", "Database connections"),
            ("queue_depth", "Queue depth"),
            ("workers", "Workers"),
            ("requests_min", "Requests per minute"),
        ],
        required=True,
        default="storage_gb",
    )
    measured_on = fields.Date(
        string="Measured On", required=True, default=fields.Date.context_today
    )
    current_value = fields.Float(string="In Use", required=True)
    capacity_value = fields.Float(string="Capacity", required=True)
    headroom_pct = fields.Float(
        string="Headroom (%)", compute="_compute_projection", store=True, digits=(16, 1)
    )
    growth_rate_pct = fields.Float(string="Growth per Month (%)", digits=(16, 1))
    projected_exhaustion = fields.Date(
        string="Projected Full", compute="_compute_projection", store=True
    )
    scaling_action = fields.Selection(
        [
            ("none", "No action"),
            ("monitor", "Monitor closely"),
            ("scale_planned", "Scale up (planned)"),
            ("scale_now", "Scale up now"),
        ],
        required=True,
        default="none",
        tracking=True,
    )
    review_note = fields.Text(string="Review Note", required=True)
    reviewed_by_id = fields.Many2one(
        "res.users", string="Reviewed By", readonly=True, default=lambda self: self.env.user
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"reviewed_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {
                "resource",
                "dimension",
                "measured_on",
                "current_value",
                "capacity_value",
                "growth_rate_pct",
            }
        return locked

    @api.depends("current_value", "capacity_value", "growth_rate_pct", "measured_on")
    def _compute_projection(self):
        for rec in self:
            cap, used = rec.capacity_value, rec.current_value
            rec.headroom_pct = round((cap - used) / cap * 100.0, 1) if cap > 0 else 0.0
            rec.projected_exhaustion = False
            growth = rec.growth_rate_pct / 100.0
            if cap > 0 and used > 0 and growth > 0 and rec.measured_on:
                if used >= cap:
                    rec.projected_exhaustion = rec.measured_on
                else:
                    months = math.log(cap / used) / math.log(1 + growth)
                    rec.projected_exhaustion = rec.measured_on + timedelta(days=int(months * 30.4))

    @api.constrains("current_value", "capacity_value", "scaling_action", "headroom_pct")
    def _check_values(self):
        for rec in self:
            if rec.capacity_value <= 0 or rec.current_value < 0:
                raise ValidationError("Capacity is above zero and use is not negative.")
            if rec.headroom_pct < 20 and rec.scaling_action == "none":
                raise ValidationError(
                    "%s has %.1f%% headroom: below 20%% a review decides to monitor or scale "
                    "(OPS-08)." % (rec.resource, rec.headroom_pct)
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The capacity review")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _sequence(self.env, "fix.capacity.metric")
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            require_platform_admin(self.env, "The capacity review")
            if _changed(self, vals, keep=("review_note", "scaling_action")):
                raise UserError(
                    "A capacity measurement is evidence: record a new review instead of "
                    "changing this one."
                )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A capacity review is evidence and is never deleted.")
        return super().unlink()
