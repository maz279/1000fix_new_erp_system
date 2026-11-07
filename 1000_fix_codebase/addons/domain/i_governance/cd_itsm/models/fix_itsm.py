# fix_itsm — M66: internal IT service management (P09-M08).
#
# A12 workflow audit (2026-11-04) M66-5 / M66-7 / M66-8 and the finish audit
# (2026-11-07) N-M66-1, N-M66-4, N-M66-5, N-M66-7, N-M66-10:
#   - every employee raises a ticket (spec s13); the requester is forced to the
#     caller's own employee, and he reads only his own tickets (record rules in
#     security/fix_itsm_m66_rules.xml). Agents read every ticket of their unit.
#   - a ticket moves through action_assign -> action_start ->
#     action_await_user <-> action_resume -> action_resolve(resolution REQUIRED)
#     -> action_close / action_reopen. Only the assignee works it; a requester
#     never resolves his own request.
#   - the SLA deadline is the catalogue item's target hours (default
#     cd_itsm.sla_default_target_hours = 8) counted on a working calendar when
#     one is set; awaiting-user time pauses the clock (BRU-ITS-19).
#   - the hourly cron_escalate_sla climbs the escalation tiers
#     (cd_itsm.sla_escalation_tiers): each pass raises the priority one step and
#     gives a real person an activity. Priority cannot be typed down afterwards.
#   - a catalogue item that requires approval gates fulfilment through M63.
#   - a major incident has a named manager and a communication cadence
#     (BRU-ITS-20); recurring incidents raise a problem (BRU-ITS-04); a dead
#     letter older than an hour raises an incident (BRU-IPF-14).
import logging
from datetime import datetime, time, timedelta

import pytz
from odoo import api, fields, models
from odoo.addons.cd_workflow_engine.models.fix_approval_engine import WEEKDAY_KEYS
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

_logger = logging.getLogger(__name__)

AGENT_GROUP = "cd_itsm.group_itsm_agent"
CHANGE_MANAGER_GROUP = "cd_itsm.group_itsm_change_manager"
CAB_GROUP = "cd_itsm.group_itsm_cab_member"
SLA_DEFAULT_HOURS_PARAM = "cd_itsm.sla_default_target_hours"
SLA_DEFAULT_HOURS = 8.0
SLA_CALENDAR_PARAM = "cd_itsm.sla_calendar_id"
SLA_ESCALATION_MANAGER_PARAM = "cd_itsm.sla_escalation_manager"
SLA_TIERS_PARAM = "cd_itsm.sla_escalation_tiers"
# Hours past the deadline at which each escalation tier falls due.
SLA_TIERS_DEFAULT = (0.0, 1.0, 8.0, 24.0)
REOPEN_DAYS_PARAM = "cd_itsm.ticket_reopen_days"
REOPEN_DAYS_DEFAULT = 7
AUTOCLOSE_DAYS_PARAM = "cd_itsm.ticket_autoclose_days"
AUTOCLOSE_DAYS_DEFAULT = 7
MAJOR_COMMS_PARAM = "cd_itsm.major_comms_hours"
MAJOR_COMMS_DEFAULT = 1
RECURRENCE_COUNT_PARAM = "cd_itsm.problem_recurrence_threshold"
RECURRENCE_COUNT_DEFAULT = 3
RECURRENCE_DAYS_PARAM = "cd_itsm.problem_recurrence_lookback_days"
RECURRENCE_DAYS_DEFAULT = 30
DEAD_LETTER_HOURS_PARAM = "cd_itsm.dead_letter_incident_hours"
DEAD_LETTER_HOURS_DEFAULT = 1.0
# Priority escalation ladder: one step up per escalation pass, never past
# 'urgent' (no fabricated severity beyond the register's own scale).
_PRIORITY_LADDER = {"low": "medium", "medium": "high", "high": "urgent"}
_PRIORITY_RANK = {"low": 0, "medium": 1, "high": 2, "urgent": 3}
_LEVELS = [("low", "Low"), ("medium", "Medium"), ("high", "High")]
# Impact x urgency decides the priority (spec s8.1).
_PRIORITY_MATRIX = {
    ("high", "high"): "urgent",
    ("high", "medium"): "high",
    ("medium", "high"): "high",
    ("high", "low"): "medium",
    ("medium", "medium"): "medium",
    ("low", "high"): "medium",
    ("medium", "low"): "low",
    ("low", "medium"): "low",
    ("low", "low"): "low",
}
OPEN_STATES = ("new", "assigned", "in_progress", "awaiting_user")
# Text that stands as the record once the ticket is finished.
_FROZEN_WHEN_DONE = {
    "title",
    "description",
    "category",
    "priority",
    "impact",
    "urgency",
    "ticket_type",
    "requester_id",
    "catalogue_id",
    "operating_unit_id",
    "problem_id",
    "ci_id",
    "caused_by_change_id",
}


def itsm_param_float(env, key, default):
    """A numeric ir.config_parameter, or the conservative default when unset."""
    raw = env["ir.config_parameter"].sudo().get_param(key)
    try:
        return float(raw) if raw not in (None, False, "") else float(default)
    except (TypeError, ValueError):
        _logger.warning("%s is not a number: %r", key, raw)
        return float(default)


def itsm_employee_of(env, user=None):
    """The active employee linked to `user` (default: the caller), read as sudo:
    a plain employee has no read access to the employee master."""
    user = user or env.user
    employees = env["hr.employee"].sudo().search([("user_id", "=", user.id)])
    company = env.company
    return employees.filtered(lambda e: e.company_id == company)[:1] or employees[:1]


def itsm_resolve_employee(env, value):
    """An employee from what a screen or a caller can send: a record, an id, an
    id typed into a prompt, an employee code, an e-mail or an exact name. Empty
    input is an empty recordset; unknown or ambiguous input is a clear refusal,
    never a TypeError."""
    Employee = env["hr.employee"].sudo()
    if not value:
        return Employee
    if isinstance(value, models.BaseModel):
        if value._name != "hr.employee":
            raise UserError("Name an employee.")
        return value.sudo()
    if isinstance(value, int):
        found = Employee.with_context(active_test=False).browse(value).exists()
    else:
        text = str(value).strip()
        if not text:
            return Employee
        if text.isdigit():
            found = Employee.with_context(active_test=False).browse(int(text)).exists()
        else:
            domain = [("name", "=ilike", text)]
            for name in ("employee_code", "work_email"):
                if name in Employee._fields:
                    domain = ["|", (name, "=ilike", text), *domain]
            found = Employee.search(domain, limit=2)
            if len(found) > 1:
                raise UserError("More than one employee matches %r: use the employee code." % text)
    if not found:
        raise UserError("No employee matches %r." % (value,))
    return found


def itsm_resolve_user(env, value):
    """A user from a record, an id or a login; an employee reference resolves to
    its linked user."""
    Users = env["res.users"].sudo()
    if not value:
        return Users
    if isinstance(value, models.BaseModel):
        if value._name == "res.users":
            return value.sudo()
        return value.sudo().user_id if value._name == "hr.employee" else Users
    text = str(value).strip()
    if text.isdigit():
        found = Users.browse(int(text)).exists()
    else:
        found = Users.search([("login", "=ilike", text)], limit=1)
    return found or itsm_resolve_employee(env, value).user_id


def itsm_activity(record, user, summary, note):
    """One open to-do per person per subject on this record: an escalation that
    repeats must not bury the person it is trying to reach."""
    if not user:
        return False
    record = record.sudo()
    already = record.activity_ids.filtered(lambda a: a.user_id == user and a.summary == summary)
    if already:
        return already[:1]
    return record.activity_schedule(
        "mail.mail_activity_data_todo",
        date_deadline=fields.Date.context_today(record),
        summary=summary,
        note=note,
        user_id=user.id,
    )


def itsm_require_superuser(env, what):
    """Cron bodies and event consumers are public methods, so JSON-RPC can reach
    them: refuse anyone but server code."""
    if not env.su:
        raise AccessError("%s runs from the server only." % what)


class FixItsmTicket(models.Model):
    _name = "fix.itsm.ticket"
    _description = "ITSM Ticket"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "create_date desc"

    # M63: a catalogue item that requires approval gates fulfilment (M66-12).
    _approval_domain = "other"
    _approval_apply_method = "_approval_grant_fulfilment"
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "New")
    title = fields.Char(required=True)
    ticket_type = fields.Selection(
        [("incident", "Incident"), ("request", "Service Request")],
        string="Ticket Type",
        required=True,
        default="incident",
        tracking=True,
        help="N-M66-10: an incident restores service; a service request fulfils a "
        "catalogue item. A ticket raised against a catalogue item is a request.",
    )
    # Not required at the column: a system-raised incident (a dead letter) has no
    # person behind it. _check_requester holds the rule for everything else.
    requester_id = fields.Many2one("hr.employee", string="Requester", index=True)
    category = fields.Selection(
        [
            ("hardware", "Hardware"),
            ("software", "Software"),
            ("network", "Network"),
            ("account", "Account/Access"),
            ("security", "Security Incident"),
            ("other", "Other"),
        ],
        required=True,
        default="software",
    )
    impact = fields.Selection(_LEVELS, required=True, default="medium", tracking=True)
    urgency = fields.Selection(_LEVELS, required=True, default="medium", tracking=True)
    priority = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")],
        default="medium",
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("assigned", "Assigned"),
            ("in_progress", "In Progress"),
            ("awaiting_user", "Awaiting User"),
            ("resolved", "Resolved"),
            ("closed", "Closed"),
            ("rejected", "Rejected"),
        ],
        default="new",
        required=True,
        tracking=True,
    )
    assigned_to = fields.Many2one("hr.employee", string="Assigned To", tracking=True)
    assigned_user_id = fields.Many2one(
        "res.users",
        string="Assigned Agent",
        readonly=True,
        copy=False,
        help="The login that works this ticket: the assignee employee's user, or the "
        "agent himself when his user carries no employee record.",
    )
    classified_by_id = fields.Many2one("res.users", string="Classified By", readonly=True)
    classified_on = fields.Datetime(readonly=True, copy=False)
    description = fields.Text(required=True)
    resolution = fields.Text()
    catalogue_id = fields.Many2one(
        "fix.itsm.catalogue",
        string="Catalogue Item",
        index=True,
        help="M66-12: the catalogue entry this request was raised against; it "
        "carries the SLA target and the approval policy.",
    )
    fulfilment_approved_by_id = fields.Many2one(
        "res.users", string="Fulfilment Approved By", readonly=True, copy=False
    )
    problem_id = fields.Many2one(
        "fix.itsm.problem",
        string="Problem",
        index=True,
        help="BRU-ITS-03: the problem record behind this incident; the incident "
        "closes when service is restored, the problem stays open until the cause "
        "is removed.",
    )
    ci_id = fields.Many2one("fix.itsm.ci", string="Configuration Item", index=True)
    caused_by_change_id = fields.Many2one("fix.itsm.change", string="Caused By Change", index=True)
    source_ref = fields.Char(
        string="System Source",
        readonly=True,
        copy=False,
        index=True,
        help="The record that raised this incident when no person did, for example "
        "fix.event.dlq,12.",
    )
    major_incident = fields.Boolean(readonly=True, copy=False, tracking=True)
    major_incident_manager_id = fields.Many2one(
        "res.users",
        string="Major Incident Manager",
        readonly=True,
        copy=False,
        tracking=True,
        help="BRU-ITS-20: the named person running this major incident.",
    )
    major_comms_every_hours = fields.Float(
        string="Communication Every (hours)", readonly=True, copy=False
    )
    major_last_comms_on = fields.Datetime(string="Last Communication", readonly=True, copy=False)
    sla_calendar_id = fields.Many2one(
        "fix.working.calendar",
        string="SLA Calendar",
        compute="_compute_sla",
        store=True,
        help="BRU-ITS-19: the working calendar the SLA counts on: the catalogue "
        "item's, else cd_itsm.sla_calendar_id, else wall-clock hours.",
    )
    sla_target_hours = fields.Float(
        compute="_compute_sla",
        store=True,
        help="The target fulfilment hours this ticket is measured against: the "
        "catalogue item's target, else the company default.",
    )
    sla_paused_hours = fields.Float(
        string="SLA Paused (hours)",
        readonly=True,
        copy=False,
        help="Hours spent awaiting the user: they do not count against the SLA.",
    )
    sla_paused_since = fields.Datetime(readonly=True, copy=False)
    sla_deadline = fields.Datetime(
        compute="_compute_sla",
        store=True,
        help="create_date + SLA target hours + paused hours, on the SLA calendar. "
        "cron_escalate_sla escalates open tickets past this moment.",
    )
    escalated = fields.Boolean(
        readonly=True,
        copy=False,
        help="Set by the SLA escalation cron when the ticket passed its deadline.",
    )
    escalation_level = fields.Integer(
        readonly=True,
        copy=False,
        default=0,
        help="How many escalation tiers this ticket has climbed.",
    )
    last_escalated_on = fields.Datetime(readonly=True, copy=False)
    resolved_on = fields.Datetime(readonly=True, copy=False)
    closed_on = fields.Datetime(readonly=True, copy=False)
    reopen_count = fields.Integer(readonly=True, copy=False, default=0)

    def init(self):
        # Rows escalated by the old one-shot cron have climbed the first tier.
        self.env.cr.execute(
            "UPDATE fix_itsm_ticket SET escalation_level = 1 "
            "WHERE escalated IS TRUE AND COALESCE(escalation_level, 0) = 0"
        )

    # ---- guards --------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "resolution",
            "escalated",
            "escalation_level",
            "last_escalated_on",
            "resolved_on",
            "closed_on",
            "assigned_to",
            "assigned_user_id",
            "classified_by_id",
            "classified_on",
            "fulfilment_approved_by_id",
            "source_ref",
            "major_incident",
            "major_incident_manager_id",
            "major_comms_every_hours",
            "major_last_comms_on",
            "sla_paused_hours",
            "sla_paused_since",
            "reopen_count",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if not self._itsm_is_agent():
            # Dropped on create too: create() forces the requester to the caller
            # and derives the priority from his stated impact and urgency.
            locked |= {"requester_id", "priority", "operating_unit_id", "problem_id", "ci_id"}
        if any(rec.state in ("closed", "rejected") for rec in self):
            locked |= _FROZEN_WHEN_DONE
        return locked

    def _itsm_is_agent(self):
        return self.env.su or self.env.user.has_group(AGENT_GROUP)

    def _assert_agent(self):
        """Only the service desk works a ticket (the audit's IT Service Desk
        role); the superuser and server code are trusted."""
        if not self._itsm_is_agent():
            raise UserError(
                "Only an ITSM agent works tickets: you do not hold the ITSM Agent group (M66-8)."
            )

    def _assert_assignee(self):
        """M66-8: the ticket is worked by its assignee. Another agent reassigns
        it first, so the register always names who holds it."""
        self._assert_agent()
        if self.env.su:
            return
        for rec in self:
            holder = rec.sudo().assigned_user_id or rec.sudo().assigned_to.user_id
            if holder and holder != self.env.user:
                raise UserError(
                    "%s is assigned to %s. Reassign it before working it (M66-8)."
                    % (rec.name, holder.name)
                )

    def _is_requester(self, user=None):
        self.ensure_one()
        user = user or self.env.user
        requester = self.sudo().requester_id
        return bool(requester and requester.user_id == user)

    @api.constrains("requester_id", "source_ref")
    def _check_requester(self):
        for rec in self:
            if not rec.requester_id and not rec.source_ref:
                raise ValidationError(
                    "Name the requester: only a system-raised incident has no person behind it."
                )

    @api.constrains("major_incident", "major_incident_manager_id")
    def _check_major_manager(self):
        for rec in self:
            if rec.major_incident and not rec.major_incident_manager_id:
                raise ValidationError("A major incident has a named incident manager (BRU-ITS-20).")

    # ---- SLA -----------------------------------------------------------------
    def _sla_calendar(self):
        self.ensure_one()
        Calendar = self.env["fix.working.calendar"].sudo()
        calendar = self.catalogue_id.sudo().calendar_id
        if calendar and calendar.active:
            return calendar
        raw = self.env["ir.config_parameter"].sudo().get_param(SLA_CALENDAR_PARAM)
        try:
            calendar = Calendar.browse(int(raw)).exists() if raw else Calendar
        except (TypeError, ValueError):
            _logger.warning("%s is not a calendar id: %r", SLA_CALENDAR_PARAM, raw)
            calendar = Calendar
        return calendar if calendar and calendar.active else Calendar

    @api.depends("catalogue_id", "create_date", "sla_paused_hours")
    def _compute_sla(self):
        default_hours = itsm_param_float(self.env, SLA_DEFAULT_HOURS_PARAM, SLA_DEFAULT_HOURS)
        Request = self.env["fix.approval.request"].sudo()
        for rec in self:
            hours = rec.catalogue_id.target_hours or default_hours
            calendar = rec._sla_calendar()
            rec.sla_target_hours = hours
            rec.sla_calendar_id = calendar
            rec.sla_deadline = (
                Request._approval_add_business_hours(
                    rec.create_date, hours + (rec.sla_paused_hours or 0.0), calendar
                )
                if rec.create_date
                else False
            )

    def _sla_hours_between(self, start, end):
        """Hours between two naive UTC moments on this ticket's SLA calendar;
        wall-clock with no calendar. A pause outside working hours costs the
        clock nothing, because the clock was not running."""
        self.ensure_one()
        if not start or not end or end <= start:
            return 0.0
        wall = (end - start).total_seconds() / 3600.0
        calendar = self.sudo().sla_calendar_id
        if not calendar:
            return wall
        rules, holidays = self.env["fix.approval.request"].sudo()._approval_calendar_rules(calendar)
        if not rules:
            return wall
        zone = pytz.timezone(calendar.timezone or "Asia/Dhaka")
        cursor = pytz.utc.localize(start).astimezone(zone).replace(tzinfo=None)
        stop = pytz.utc.localize(end).astimezone(zone).replace(tzinfo=None)
        total = timedelta(0)
        day = cursor.date()
        while day <= stop.date():
            if not any(d_from <= day <= d_to for d_from, d_to in holidays):
                midnight = datetime.combine(day, time.min)
                for hour_from, hour_to in rules.get(WEEKDAY_KEYS[day.weekday()], ()):
                    begin = max(cursor, midnight + timedelta(hours=hour_from))
                    finish = min(stop, midnight + timedelta(hours=hour_to))
                    if finish > begin:
                        total += finish - begin
            day += timedelta(days=1)
        return total.total_seconds() / 3600.0

    def _sla_pause_closed_vals(self):
        """Vals that end a running pause and credit it to the clock."""
        self.ensure_one()
        vals = {"sla_paused_since": False}
        if self.sla_paused_since:
            vals["sla_paused_hours"] = (self.sla_paused_hours or 0.0) + self._sla_hours_between(
                self.sla_paused_since, fields.Datetime.now()
            )
        return vals

    # ---- create --------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        is_agent = self._itsm_is_agent()
        caller = itsm_employee_of(self.env)
        unit = self.env.user.sudo().default_operating_unit_id if not self.env.su else None
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("fix.itsm.ticket") or "ITSM/New"
            if not is_agent:
                # N-M66-1: an employee raises his own ticket; nobody else's.
                if not caller:
                    raise UserError(
                        "Your login is not linked to an employee record, so the ticket has "
                        "no requester. Ask HR to link it, or call the service desk."
                    )
                vals["requester_id"] = caller.id
                for name in (
                    "priority",
                    "company_id",
                    "operating_unit_id",
                    "problem_id",
                    "ci_id",
                    "caused_by_change_id",
                ):
                    vals.pop(name, None)
            elif not vals.get("requester_id") and not vals.get("source_ref") and caller:
                vals["requester_id"] = caller.id
            if not vals.get("operating_unit_id") and unit:
                vals["operating_unit_id"] = unit.id
            if not vals.get("priority"):
                vals["priority"] = _PRIORITY_MATRIX[
                    (vals.get("impact") or "medium", vals.get("urgency") or "medium")
                ]
            if vals.get("catalogue_id") and "ticket_type" not in vals:
                vals["ticket_type"] = "request"
        recs = super().create(vals_list)
        for rec in recs:
            publish(
                self.env,
                "itsm.ticket_created",
                "fix.itsm.ticket",
                rec.id,
                {"title": rec.title, "priority": rec.priority},
            )
            if rec.sudo().catalogue_id.requires_approval:
                rec.sudo()._fulfilment_route(quiet=True)
        recs.sudo().mapped("problem_id")._on_incident_linked()
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            if "priority" in vals:
                # M66-7: the SLA raised it; nobody types it back down.
                wanted = _PRIORITY_RANK.get(vals["priority"], 0)
                for rec in self:
                    if rec.escalated and wanted < _PRIORITY_RANK.get(rec.priority, 0):
                        raise UserError(
                            "%s was escalated by the SLA to %s: its priority cannot be lowered."
                            % (rec.name, rec.priority)
                        )
            frozen = _FROZEN_WHEN_DONE & set(vals)
            if frozen and any(rec.state in ("closed", "rejected") for rec in self):
                raise UserError("A closed ticket stands as the record: reopen it to change it.")
        result = super().write(vals)
        if vals.get("problem_id"):
            self.sudo().mapped("problem_id")._on_incident_linked()
        return result

    # ---- M63 fulfilment gate (M66-12) ----------------------------------------
    def _approval_group_xmlid(self):
        return CHANGE_MANAGER_GROUP

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return bool(self.sudo().catalogue_id.requires_approval)

    def _approval_excluded(self):
        self.ensure_one()
        return super()._approval_excluded() | self.sudo().requester_id.user_id

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {
            "title",
            "description",
            "catalogue_id",
            "requester_id",
        }

    def _approval_grant_fulfilment(self):
        """The engine's apply method: runs in the approver's env, from the inbox
        task only."""
        self._approval_assert_routed()
        for rec in self:
            rec._guarded().write({"fulfilment_approved_by_id": rec._approval_authority_user().id})

    def _approval_on_rejected(self, comment):
        self.sudo()._guarded().write({"state": "rejected", "closed_on": fields.Datetime.now()})
        for rec in self.sudo():
            itsm_activity(
                rec,
                rec.requester_id.user_id,
                "Request refused: %s" % rec.name,
                "Your request was refused: %s" % (comment or "no reason given"),
            )

    def _fulfilment_route(self, quiet=False):
        """Route the request to its approver. With nobody to route to, a raised
        request stays visible and the desk is told: raising it must not fail."""
        for rec in self:
            try:
                with self.env.cr.savepoint():
                    rec.action_request_approval()
            except UserError as exc:
                if not quiet:
                    raise
                rec.message_post(body="Approval could not be routed yet: %s" % exc)

    def _assert_fulfilment_approved(self):
        for rec in self:
            item = rec.sudo().catalogue_id
            if item.requires_approval and rec.sudo().approval_state != "approved":
                raise UserError(
                    "%s is a catalogue item that requires approval (%s). It cannot be fulfilled "
                    "until the approver signs it off (approval: %s)."
                    % (rec.name, item.name, rec.sudo().approval_state)
                )

    def action_request_fulfilment(self):
        """Requester or desk asks for the approval the catalogue item requires."""
        for rec in self:
            if not (rec._itsm_is_agent() or rec._is_requester()):
                raise UserError("Approval is requested by the requester or the service desk.")
            if rec.state != "new":
                raise UserError("Approval is requested before a ticket is taken on.")
            if not rec.sudo().catalogue_id.requires_approval:
                raise UserError("This catalogue item needs no approval.")
            if rec.sudo().approval_state in ("pending", "approved"):
                raise UserError("Approval is already %s." % rec.sudo().approval_state)
            rec.sudo()._fulfilment_route()

    # ---- the working lifecycle -----------------------------------------------
    def _assignee_for(self, named):
        """(employee, user) that takes the ticket: the named agent, else the one
        already on the ticket, else the clicking agent. An agent whose user
        carries no employee record still takes it himself (N-M66-5)."""
        self.ensure_one()
        employee = named or self.sudo().assigned_to or itsm_employee_of(self.env)
        if employee:
            user = employee.user_id
        elif self.env.su:
            raise UserError("Name the agent to assign the ticket to.")
        else:
            user = self.env.user
        if not self.env.su:
            if employee and not employee.active:
                raise UserError("%s is not an active employee." % employee.name)
            if not user or not user.active or not user.has_group(AGENT_GROUP):
                raise UserError(
                    "%s does not hold the ITSM Agent group: only the service desk "
                    "takes a ticket." % (employee.name if employee else user.name)
                )
        return employee, user

    def action_assign(self, assigned_to=None):
        """The assignment step (I3). `assigned_to` is an employee: a record, or
        what the JSON endpoint and the prompt send (an id, a code, a name). Blank
        means the clicking agent."""
        self._assert_agent()
        named = itsm_resolve_employee(self.env, assigned_to)
        for rec in self:
            if rec.state != "new":
                raise UserError("Only a new ticket can be assigned. Use Reassign.")
            rec._assert_fulfilment_approved()
            employee, user = rec._assignee_for(named)
            rec._guarded().write(
                {
                    "state": "assigned",
                    "assigned_to": employee.id or False,
                    "assigned_user_id": user.id or False,
                }
            )
            rec.sudo().message_post(
                body="Assigned to %s by %s." % (employee.name or user.name, self.env.user.name)
            )
            if user and user != self.env.user:
                itsm_activity(rec, user, "Assigned to you: %s" % rec.name, rec.title or rec.name)

    def action_reassign(self, assigned_to=None):
        """Hand a ticket already taken on to another agent; the register always
        names who holds it."""
        self._assert_agent()
        named = itsm_resolve_employee(self.env, assigned_to)
        if not named:
            raise UserError("Name the agent to hand the ticket to.")
        for rec in self:
            if rec.state not in ("assigned", "in_progress", "awaiting_user"):
                raise UserError("Reassign a ticket that is being worked.")
            employee, user = rec._assignee_for(named)
            rec._guarded().write(
                {"assigned_to": employee.id or False, "assigned_user_id": user.id or False}
            )
            rec.sudo().message_post(
                body="Reassigned to %s by %s." % (employee.name, self.env.user.name)
            )
            if user and user != self.env.user:
                itsm_activity(rec, user, "Assigned to you: %s" % rec.name, rec.title or rec.name)

    def action_classify(self, impact=None, urgency=None, ticket_type=None):
        """Triage: impact x urgency sets the priority (I2). Priority never drops
        below what the SLA already raised it to. Arguments left out keep what the
        form holds."""
        self._assert_agent()
        for arg in (impact, urgency):
            if arg and arg not in dict(_LEVELS):
                raise UserError("Impact and urgency are low, medium or high.")
        if ticket_type and ticket_type not in ("incident", "request"):
            raise UserError("A ticket is an incident or a service request.")
        for rec in self:
            if rec.state not in OPEN_STATES:
                raise UserError("Classify an open ticket.")
            new_impact = impact or rec.impact
            new_urgency = urgency or rec.urgency
            priority = _PRIORITY_MATRIX[(new_impact, new_urgency)]
            if rec.escalated and _PRIORITY_RANK[priority] < _PRIORITY_RANK[rec.priority]:
                priority = rec.priority
            vals = {
                "impact": new_impact,
                "urgency": new_urgency,
                "priority": priority,
                "classified_by_id": self.env.uid,
                "classified_on": fields.Datetime.now(),
            }
            if ticket_type:
                vals["ticket_type"] = ticket_type
            rec._guarded().write(vals)
            rec.sudo().message_post(
                body="Classified by %s: impact %s, urgency %s, priority %s."
                % (self.env.user.name, new_impact, new_urgency, priority)
            )

    def action_start(self):
        self._assert_assignee()
        for rec in self:
            if rec.state != "assigned":
                raise UserError("Only an assigned ticket can move to in progress.")
            rec._guarded().write({"state": "in_progress"})

    def action_await_user(self, reason=None):
        """Waiting on the requester: the SLA clock stops (BRU-ITS-19)."""
        self._assert_assignee()
        if not (reason or "").strip():
            raise UserError("Say what you need from the user: the reason is required.")
        for rec in self:
            if rec.state not in ("assigned", "in_progress"):
                raise UserError("Only a ticket being worked can wait on the user.")
            rec._guarded().write(
                {"state": "awaiting_user", "sla_paused_since": fields.Datetime.now()}
            )
            rec.sudo().message_post(body="Awaiting the user (SLA paused): %s" % reason)
            itsm_activity(
                rec,
                rec.sudo().requester_id.user_id,
                "IT needs your answer: %s" % rec.name,
                reason,
            )

    def action_resume(self):
        """The user answered: the clock runs again, the pause credited to it.
        The requester may press it himself (his answer is the whole point)."""
        for rec in self:
            if rec.state != "awaiting_user":
                raise UserError("Resume a ticket that is awaiting the user.")
            if rec._is_requester():
                target = rec.sudo()
            else:
                rec._assert_assignee()
                target = rec
            vals = target._sla_pause_closed_vals()
            vals["state"] = "in_progress"
            target._guarded().write(vals)
            target.sudo().message_post(body="%s resumed the ticket." % self.env.user.name)

    def action_resolve(self, resolution=None):
        self._assert_agent()
        for rec in self:
            if rec.state in ("resolved", "closed"):
                raise UserError("Ticket already resolved")
            if rec.state not in ("assigned", "in_progress"):
                raise UserError(
                    "Assign the ticket and start work before resolving it (M66-8): "
                    "a request the service desk never took on cannot be resolved."
                )
            rec._assert_assignee()
            rec._assert_fulfilment_approved()
            if not self.env.su and rec._is_requester():
                raise UserError(
                    "You raised %s: another agent resolves it (M66-8 segregation of duties)."
                    % rec.name
                )
            if not (resolution or "").strip():
                raise UserError("Record what resolved the ticket: the resolution is required.")
            rec._guarded().write(
                {
                    "state": "resolved",
                    "resolution": resolution,
                    "resolved_on": fields.Datetime.now(),
                }
            )
            publish(
                self.env, "itsm.ticket_resolved", "fix.itsm.ticket", rec.id, {"ticket": rec.name}
            )

    def action_close(self):
        """The requester's confirmation closes a resolved ticket (I6); the desk
        may also close it. An employee holds no write access, so the transition
        runs as sudo once he is proven to be the requester (N-M66-4)."""
        for rec in self:
            if rec.state != "resolved":
                raise UserError("Only a resolved ticket can be closed.")
            if not rec._itsm_is_agent() and not rec._is_requester():
                raise UserError("A resolved ticket is closed by its requester or the service desk.")
            rec.sudo()._guarded().write({"state": "closed", "closed_on": fields.Datetime.now()})
            rec.sudo().message_post(body="Closed by %s." % self.env.user.name)

    def action_reopen(self, reason=None):
        """The requester rejects the resolution within the window (default 7 days
        from the resolution, cd_itsm.ticket_reopen_days). The ticket goes back to
        its agent; the time it sat resolved does not count against the SLA."""
        days = itsm_param_float(self.env, REOPEN_DAYS_PARAM, REOPEN_DAYS_DEFAULT)
        if not (reason or "").strip():
            raise UserError("Say why the ticket is not fixed: the reason is required.")
        now = fields.Datetime.now()
        for rec in self:
            if rec.state not in ("resolved", "closed"):
                raise UserError("Reopen a resolved or closed ticket.")
            if not rec._itsm_is_agent() and not rec._is_requester():
                raise UserError("A ticket is reopened by its requester or the service desk.")
            if rec.resolved_on and rec.resolved_on + timedelta(days=days) < now:
                raise UserError(
                    "%s was resolved on %s: the %d-day reopen window has passed. Raise a new "
                    "ticket." % (rec.name, str(rec.resolved_on)[:10], days)
                )
            target = rec.sudo()
            holder = target.assigned_user_id or target.assigned_to.user_id
            target._guarded().write(
                {
                    "state": "in_progress" if holder or target.assigned_to else "new",
                    "resolution": False,
                    "resolved_on": False,
                    "closed_on": False,
                    "reopen_count": target.reopen_count + 1,
                    "sla_paused_hours": (target.sla_paused_hours or 0.0)
                    + target._sla_hours_between(rec.resolved_on, now),
                }
            )
            target.message_post(
                body="Reopened by %s: %s (the previous resolution stands in this trail)."
                % (self.env.user.name, reason)
            )
            itsm_activity(target, holder, "Reopened: %s" % target.name, reason)

    # ---- major incident (BRU-ITS-20) -----------------------------------------
    def action_declare_major(self, manager=None):
        """A major incident has a NAMED manager and a communication cadence."""
        self._assert_agent()
        person = itsm_resolve_user(self.env, manager)
        if not person:
            raise UserError("Name the major incident manager (BRU-ITS-20).")
        if not person.active or not person.has_group(AGENT_GROUP):
            raise UserError("%s does not hold the ITSM Agent group." % person.name)
        cadence = itsm_param_float(self.env, MAJOR_COMMS_PARAM, MAJOR_COMMS_DEFAULT)
        for rec in self:
            if rec.state not in OPEN_STATES:
                raise UserError("Declare a major incident on an open ticket.")
            if rec.ticket_type != "incident":
                raise UserError("Only an incident can be declared major.")
            rec._guarded().write(
                {
                    "major_incident": True,
                    "major_incident_manager_id": person.id,
                    "major_comms_every_hours": cadence,
                    "major_last_comms_on": fields.Datetime.now(),
                    "priority": "urgent",
                }
            )
            rec.sudo().message_post(
                body="Declared a major incident by %s; incident manager: %s; communication "
                "every %.1f h." % (self.env.user.name, person.name, cadence)
            )
            itsm_activity(
                rec,
                person,
                "Major incident: %s" % rec.name,
                "You are the named incident manager for %s." % rec.title,
            )

    def action_major_update(self, note=None):
        """The communication to affected users; resets the cadence clock."""
        self._assert_agent()
        if not (note or "").strip():
            raise UserError("Write the update for the affected users.")
        for rec in self:
            if not rec.major_incident:
                raise UserError("%s is not a major incident." % rec.name)
            rec._guarded().write({"major_last_comms_on": fields.Datetime.now()})
            rec.sudo().message_post(body="Major incident update: %s" % note)

    # ---- incident to problem (BRU-ITS-03/04) ---------------------------------
    def action_raise_problem(self):
        """Raise the problem behind this incident and link it."""
        self._assert_agent()
        for rec in self:
            if rec.problem_id:
                raise UserError("%s is already linked to %s." % (rec.name, rec.problem_id.name))
            problem = self.env["fix.itsm.problem"].create(
                {
                    "title": rec.title,
                    "description": rec.description,
                    "severity": {"urgent": "critical"}.get(rec.priority, rec.priority),
                    "owner_id": self.env.uid,
                }
            )
            rec.write({"problem_id": problem.id})
            rec.sudo().message_post(body="Problem %s raised from this incident." % problem.name)

    # ---- the service desk queue ----------------------------------------------
    @api.model
    def _queue_agents(self, company=None):
        """Who stands behind an unassigned ticket: active holders of the agent
        group in the company, real people before the built-in admin."""
        group = self.env.ref(AGENT_GROUP, raise_if_not_found=False)
        if not group:
            return self.env["res.users"]
        company = company or self.env.company
        holders = (
            group.sudo()
            .all_user_ids.filtered(
                lambda u: u.active and not u.share and company in u.company_ids and u.id != 1
            )
            .sudo()
        )
        admin = self.env.ref("base.user_admin", raise_if_not_found=False)
        return ((holders - admin) or holders) if admin else holders

    def _queue_owner(self):
        """One accountable agent per unassigned ticket, rotated by ticket id, so
        the whole queue is spread across the desk and no ticket has nobody."""
        self.ensure_one()
        agents = self._queue_agents(self.sudo().company_id)
        if self.sudo().category == "security":
            # A security incident is masked from the desk: only those who may read
            # it can be the ones told about it.
            managers = self.env.ref(CHANGE_MANAGER_GROUP).sudo().all_user_ids
            managers |= self.env.ref(CAB_GROUP).sudo().all_user_ids
            agents = agents & managers
        agents = agents.sorted("id") - self.sudo().requester_id.user_id
        return agents[self.id % len(agents)] if agents else self.env["res.users"]

    # ---- crons ---------------------------------------------------------------
    @api.model
    def _sla_tiers(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(SLA_TIERS_PARAM)
        if not raw:
            return SLA_TIERS_DEFAULT
        try:
            tiers = sorted(float(x) for x in str(raw).split(",") if str(x).strip())
        except (TypeError, ValueError):
            _logger.warning("%s is not a list of hours: %r", SLA_TIERS_PARAM, raw)
            return SLA_TIERS_DEFAULT
        return tuple(tiers) or SLA_TIERS_DEFAULT

    @api.model
    def cron_escalate_sla(self):
        """Hourly: climb the escalation tiers for tickets past their deadline.

        Each pass raises one tier that is due: the priority goes up one step and
        a real person gets an activity. That is the assignee, or for an unassigned
        ticket the agent the queue rotates it to, plus the named manager
        (cd_itsm.sla_escalation_manager, a login) when one is set. An awaiting-user
        ticket is paused and is not escalated.

        A12 P2: this cron is the shipped feature-flag kill switch
        (fix.feature.flag key `itsm.sla_auto_escalate`, read with is_disabled,
        presence-based opt-out)."""
        itsm_require_superuser(self.env, "SLA escalation")
        if self.env["fix.feature.flag"].is_disabled("itsm.sla_auto_escalate"):
            _logger.info("SLA auto-escalation skipped: kill switch itsm.sla_auto_escalate")
            return True
        now = fields.Datetime.now()
        tiers = self._sla_tiers()
        late = self.sudo().search(
            [
                ("state", "in", ("new", "assigned", "in_progress")),
                ("sla_deadline", "!=", False),
                ("sla_deadline", "<", now),
                ("escalation_level", "<", len(tiers)),
            ]
        )
        manager = self._sla_escalation_manager()
        labels = dict(self._fields["priority"].selection)
        for ticket in late:
            overdue = (now - ticket.sla_deadline).total_seconds() / 3600.0
            due = sum(1 for hours in tiers if hours <= overdue)
            level = ticket.escalation_level or 0
            if level >= due:
                continue
            level += 1
            priority = _PRIORITY_LADDER.get(ticket.priority, ticket.priority)
            ticket._guarded().write(
                {
                    "escalated": True,
                    "escalation_level": level,
                    "last_escalated_on": now,
                    "priority": priority,
                }
            )
            holder = ticket.assigned_user_id or ticket.assigned_to.user_id
            people = (holder or ticket._queue_owner()) | manager
            ticket.message_post(
                body="SLA breach, tier %d: past the %.1f h target (deadline %s) by %.1f h; "
                "priority raised to %s; told: %s."
                % (
                    level,
                    ticket.sla_target_hours,
                    ticket.sla_deadline,
                    overdue,
                    labels.get(priority),
                    ", ".join(people.mapped("name")) or "nobody, no agent holds the queue",
                )
            )
            note = "Ticket %s passed its SLA deadline and is at escalation tier %d." % (
                ticket.display_name,
                level,
            )
            for user in people:
                itsm_activity(ticket, user, "SLA breach on %s" % ticket.name, note)
        self._chase_major_comms(now)
        return True

    @api.model
    def _chase_major_comms(self, now):
        majors = self.sudo().search([("major_incident", "=", True), ("state", "in", OPEN_STATES)])
        for ticket in majors:
            every = ticket.major_comms_every_hours or MAJOR_COMMS_DEFAULT
            last = ticket.major_last_comms_on
            if last and last + timedelta(hours=every) <= now:
                itsm_activity(
                    ticket,
                    ticket.major_incident_manager_id,
                    "Update due: %s" % ticket.name,
                    "The affected users are owed an update on this major incident.",
                )

    @api.model
    def _sla_escalation_manager(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(SLA_ESCALATION_MANAGER_PARAM)
        if not raw:
            return self.env["res.users"]
        manager = self.env["res.users"].sudo().search([("login", "=", raw.strip())], limit=1)
        return manager if manager and manager.active else self.env["res.users"]

    @api.model
    def cron_ticket_housekeeping(self):
        """Daily: auto-close tickets resolved longer than the window, and raise a
        problem for incidents that keep recurring (BRU-ITS-04)."""
        itsm_require_superuser(self.env, "Ticket housekeeping")
        days = itsm_param_float(self.env, AUTOCLOSE_DAYS_PARAM, AUTOCLOSE_DAYS_DEFAULT)
        cutoff = fields.Datetime.now() - timedelta(days=days)
        stale = self.sudo().search([("state", "=", "resolved"), ("resolved_on", "<", cutoff)])
        for ticket in stale:
            ticket._guarded().write({"state": "closed", "closed_on": fields.Datetime.now()})
            ticket.message_post(
                body="Closed automatically: resolved more than %d days ago with no objection."
                % days
            )
        self._raise_recurring_problems()
        return len(stale)

    @api.model
    def _raise_recurring_problems(self):
        """BRU-ITS-04: incidents on one CI or catalogue item above the threshold
        inside the lookback window raise a problem and link to it."""
        threshold = int(
            itsm_param_float(self.env, RECURRENCE_COUNT_PARAM, RECURRENCE_COUNT_DEFAULT)
        )
        days = itsm_param_float(self.env, RECURRENCE_DAYS_PARAM, RECURRENCE_DAYS_DEFAULT)
        since = fields.Datetime.now() - timedelta(days=days)
        tickets = self.sudo().search(
            [
                ("ticket_type", "=", "incident"),
                ("problem_id", "=", False),
                ("create_date", ">=", since),
                "|",
                ("ci_id", "!=", False),
                ("catalogue_id", "!=", False),
            ]
        )
        groups = {}
        for ticket in tickets:
            key = ("ci", ticket.ci_id.id) if ticket.ci_id else ("cat", ticket.catalogue_id.id)
            groups[key] = groups.get(key, self.browse()) | ticket
        raised = self.env["fix.itsm.problem"]
        for (kind, _id), group in groups.items():
            if len(group) < threshold:
                continue
            first = group[0]
            subject = first.ci_id.name if kind == "ci" else first.catalogue_id.name
            problem = (
                self.env["fix.itsm.problem"]
                .sudo()
                .create(
                    {
                        "title": "Recurring incidents on %s" % subject,
                        "description": "Raised automatically: %d incidents in %d days (%s)."
                        % (len(group), days, ", ".join(group.mapped("name"))[:300]),
                        "severity": "high",
                        "company_id": first.company_id.id,
                    }
                )
            )
            group.write({"problem_id": problem.id})
            raised |= problem
        return raised

    @api.model
    def cron_dead_letter_incidents(self):
        """BRU-IPF-14: a real dead letter older than the limit (default one hour)
        is an incident, from the relay or the webhook dispatcher. One incident per
        dead letter, whatever calls this; rows seeded with no delivery behind them
        are not incidents."""
        itsm_require_superuser(self.env, "The dead-letter incident cron")
        Dlq = self.env["fix.event.dlq"].sudo()
        Dlq.cron_sync_dead_letters()
        hours = itsm_param_float(self.env, DEAD_LETTER_HOURS_PARAM, DEAD_LETTER_HOURS_DEFAULT)
        cutoff = fields.Datetime.now() - timedelta(hours=hours)
        letters = Dlq.search(
            [
                ("state", "=", "pending"),
                "|",
                ("delivery_id", "!=", False),
                ("webhook_delivery_id", "!=", False),
                ("created_at", "<", cutoff),
            ]
        )
        refs = {"fix.event.dlq,%d" % letter.id: letter for letter in letters}
        known = set(self.sudo().search([("source_ref", "in", list(refs))]).mapped("source_ref"))
        created = self.browse()
        for ref, letter in refs.items():
            if ref in known:
                continue
            created |= self.sudo().create(
                {
                    "title": ("Dead letter: %s" % letter.topic_code)[:200],
                    "description": "Event topic %s dead-lettered after %d attempts on %s.\n"
                    "Reason: %s\nReplay it from the DLQ screen once the cause is fixed."
                    % (letter.topic_code, letter.attempts, letter.created_at, letter.reason),
                    "category": "software",
                    "ticket_type": "incident",
                    "impact": "medium",
                    "urgency": "high",
                    "source_ref": ref,
                    "company_id": letter.company_id.id,
                }
            )
        return created

    # ---- event consumers (A12 P2 hand-offs; FF-48) ---------------------------
    # The relay calls these as superuser; they stay idempotent. A consumer that
    # only wrote on its own chatter proved nothing (M66-13): each one now tells a
    # person what the event means for him.
    @api.model
    def consume_ticket_created(self, event):
        """itsm.ticket_created: the unassigned ticket lands on a named agent."""
        itsm_require_superuser(self.env, "The ticket consumer")
        ticket = self.browse(event.get("aggregate_id") or 0).exists()
        if ticket and ticket.state == "new":
            person = ticket._queue_owner()
            itsm_activity(
                ticket,
                person,
                "New ticket in the queue: %s" % ticket.name,
                ticket.title or ticket.name,
            )
            ticket.message_post(
                body="Handed to the service desk queue: %s (event %s)."
                % (person.name or "no agent holds the queue", event.get("event_id"))
            )
        return True

    @api.model
    def consume_ticket_resolved(self, event):
        """itsm.ticket_resolved: the requester is told to confirm or reopen."""
        itsm_require_superuser(self.env, "The ticket consumer")
        ticket = self.browse(event.get("aggregate_id") or 0).exists()
        if ticket and ticket.state == "resolved":
            requester = ticket.requester_id.user_id
            days = itsm_param_float(self.env, REOPEN_DAYS_PARAM, REOPEN_DAYS_DEFAULT)
            itsm_activity(
                ticket,
                requester,
                "Please confirm the fix: %s" % ticket.name,
                "Close the ticket if it is fixed, or reopen it within %d days." % days,
            )
            ticket.message_post(
                body="Resolution handed to %s to confirm (event %s)."
                % (requester.name or "the requester, who has no login,", event.get("event_id"))
            )
        return True

    @api.model
    def consume_relay_unhealthy(self, event):
        """outbox.relay_unhealthy: the relay names its dead letters; each one
        older than the limit becomes an incident (M28 to M66, BRU-IPF-14)."""
        itsm_require_superuser(self.env, "The relay health consumer")
        return len(self.cron_dead_letter_incidents())
