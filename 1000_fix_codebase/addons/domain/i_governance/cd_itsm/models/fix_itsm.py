# fix_itsm — M66: internal IT service management (P09-M08).
#
# A12 workflow audit (2026-11-04) M66-5 / M66-7 / M66-8: the ticket had no
# SLA clock, no assignment step, no escalation cron; the requester resolved
# his own unassigned ticket with an empty resolution, and state/resolution
# were plain writes. Now:
#   - states are guarded (fix.guarded.mixin): a ticket moves through
#     action_assign -> action_start -> action_resolve(resolution REQUIRED)
#     -> action_close;
#   - the SLA deadline is computed from the catalogue item's target hours
#     (config default cd_itsm.sla_default_target_hours = 8) and the hourly
#     cron_escalate_sla() escalates tickets past it: priority raised one
#     step, escalated flag set, the escalation manager notified — the
#     recipient is a config parameter, never invented.
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

_logger = logging.getLogger(__name__)

AGENT_GROUP = "cd_itsm.group_itsm_agent"
SLA_DEFAULT_HOURS_PARAM = "cd_itsm.sla_default_target_hours"
SLA_DEFAULT_HOURS = 8.0
SLA_ESCALATION_MANAGER_PARAM = "cd_itsm.sla_escalation_manager"
# priority escalation ladder: one step up per escalation pass, never past
# 'urgent' (no fabricated severity beyond the register's own scale).
_PRIORITY_LADDER = {"low": "medium", "medium": "high", "high": "urgent"}


class FixItsmTicket(models.Model):
    _name = "fix.itsm.ticket"
    _description = "ITSM Ticket"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "New")
    title = fields.Char(required=True)
    requester_id = fields.Many2one("hr.employee", string="Requester", required=True)
    category = fields.Selection(
        [
            ("hardware", "Hardware"),
            ("software", "Software"),
            ("network", "Network"),
            ("account", "Account/Access"),
            ("other", "Other"),
        ],
        required=True,
        default="software",
    )
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
            ("resolved", "Resolved"),
            ("closed", "Closed"),
        ],
        default="new",
        required=True,
        tracking=True,
    )
    assigned_to = fields.Many2one("hr.employee", string="Assigned To")
    description = fields.Text(required=True)
    resolution = fields.Text()
    catalogue_id = fields.Many2one(
        "fix.itsm.catalogue",
        string="Catalogue Item",
        index=True,
        help="M66-12: the catalogue entry this request was raised against; it "
        "carries the SLA target and the approval policy.",
    )
    sla_target_hours = fields.Float(
        compute="_compute_sla",
        store=True,
        help="The target fulfilment hours this ticket is measured against: the "
        "catalogue item's target, else the company default.",
    )
    sla_deadline = fields.Datetime(
        compute="_compute_sla",
        store=True,
        help="create_date + SLA target hours. cron_escalate_sla escalates open "
        "tickets past this moment.",
    )
    escalated = fields.Boolean(
        readonly=True,
        copy=False,
        help="Set by the SLA escalation cron when the ticket passed its deadline.",
    )
    resolved_on = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "resolution", "escalated", "resolved_on"}

    @api.depends("catalogue_id", "create_date")
    def _compute_sla(self):
        default_hours = SLA_DEFAULT_HOURS
        try:
            raw = self.env["ir.config_parameter"].sudo().get_param(SLA_DEFAULT_HOURS_PARAM)
            default_hours = float(raw) if raw else SLA_DEFAULT_HOURS
        except (TypeError, ValueError):
            default_hours = SLA_DEFAULT_HOURS
        for rec in self:
            hours = rec.catalogue_id.target_hours or default_hours
            rec.sla_target_hours = hours
            rec.sla_deadline = (
                rec.create_date + timedelta(hours=hours) if rec.create_date else False
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("fix.itsm.ticket") or "ITSM/New"
        recs = super().create(vals_list)
        for rec in recs:
            publish(
                self.env,
                "itsm.ticket_created",
                "fix.itsm.ticket",
                rec.id,
                {"title": rec.title, "priority": rec.priority},
            )
        return recs

    def _assert_agent(self):
        """Only the service desk works a ticket (the audit's IT Service Desk
        role); the superuser and server code are trusted."""
        if not self.env.su and not self.env.user.has_group(AGENT_GROUP):
            raise UserError(
                "Only an ITSM agent works tickets: you do not hold the ITSM Agent " "group (M66-8)."
            )

    def action_assign(self, assigned_to=None):
        """The assignment step the lifecycle was missing (I3)."""
        self._assert_agent()
        for rec in self:
            if rec.state != "new":
                raise UserError("Only a new ticket can be assigned.")
            employee = assigned_to or self.env.user.employee_ids[:1]
            if not employee:
                raise UserError(
                    "Name the agent to assign the ticket to (your user carries no " "employee)."
                )
            rec._guarded().write({"state": "assigned", "assigned_to": employee.id})

    def action_start(self):
        self._assert_agent()
        for rec in self:
            if rec.state != "assigned":
                raise UserError("Only an assigned ticket can move to in progress.")
            rec._guarded().write({"state": "in_progress"})

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
        """The requester's confirmation closes a resolved ticket (I6)."""
        for rec in self:
            if rec.state != "resolved":
                raise UserError("Only a resolved ticket can be closed.")
            requester_user = rec.requester_id.sudo().user_id
            if (
                not self.env.su
                and self.env.user != requester_user
                and not self.env.user.has_group(AGENT_GROUP)
            ):
                raise UserError("A resolved ticket is closed by its requester or the service desk.")
            rec._guarded().write({"state": "closed"})

    # ---- SLA escalation (R3 / M66-7) ---------------------------------------
    @api.model
    def cron_escalate_sla(self):
        """Escalate open tickets past their SLA deadline (hourly ir.cron
        fix.itsm.ticket shipped by the lead).

        Escalation raises the priority one step, flags the ticket and leaves
        a trail; notifying a manager needs a NAMED recipient, which is a
        business appointment: cd_itsm.sla_escalation_manager (a login) says
        who is told. Unset = nobody is messaged, the flag and priority still
        apply — no recipient is ever invented.

        A12 P2: this cron is the shipped feature-flag kill switch
        (fix.feature.flag key `itsm.sla_auto_escalate`, read with
        is_disabled — presence-based opt-out). Escalation, which the audit
        mandates, runs by default; an operator can switch it off without a
        deployment — the BRU-ADM-09/10 claim made real."""
        if self.env["fix.feature.flag"].is_disabled("itsm.sla_auto_escalate"):
            _logger.info("SLA auto-escalation skipped: kill switch itsm.sla_auto_escalate")
            return True
        now = fields.Datetime.now()
        late = self.sudo().search(
            [
                ("state", "in", ("new", "assigned", "in_progress")),
                ("escalated", "=", False),
                ("sla_deadline", "!=", False),
                ("sla_deadline", "<", now),
            ]
        )
        if not late:
            return True
        manager = self._sla_escalation_manager()
        for ticket in late:
            ticket.sudo()._guarded().write(
                {
                    "escalated": True,
                    "priority": _PRIORITY_LADDER.get(ticket.priority, ticket.priority),
                }
            )
            ticket.message_post(
                body="SLA breach: ticket is past its target of %.1f h (deadline %s); "
                "priority raised to %s."
                % (
                    ticket.sla_target_hours,
                    ticket.sla_deadline,
                    dict(self._fields["priority"].selection).get(
                        _PRIORITY_LADDER.get(ticket.priority, ticket.priority)
                    ),
                )
            )
            if manager:
                ticket.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=fields.Date.context_today(ticket),
                    summary="SLA breach on %s" % ticket.name,
                    note="Ticket %s passed its SLA deadline and was escalated."
                    % ticket.display_name,
                    user_id=manager.id,
                )
        return True

    @api.model
    def _sla_escalation_manager(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(SLA_ESCALATION_MANAGER_PARAM)
        if not raw:
            return self.env["res.users"]
        manager = self.env["res.users"].sudo().search([("login", "=", raw.strip())], limit=1)
        return manager if manager and manager.active else self.env["res.users"]

    # ---- event consumers (A12 P2 hand-offs; FF-48) -------------------------
    # The fix.event.consumer data records ship in cd_itsm/data/ (lead-owned
    # file, see the build's Needs list). The relay calls these as superuser;
    # they stay idempotent.
    @api.model
    def consume_ticket_created(self, event):
        """itsm.ticket_created: the ticket's own trail of the hand-off."""
        ticket = self.browse(event.get("aggregate_id") or 0).exists()
        if ticket:
            ticket.message_post(
                body="Creation handed to downstream consumers (event %s)." % event.get("event_id")
            )
        return True

    @api.model
    def consume_ticket_resolved(self, event):
        """itsm.ticket_resolved: the closure hand-off trail."""
        ticket = self.browse(event.get("aggregate_id") or 0).exists()
        if ticket:
            ticket.message_post(
                body="Resolution handed to downstream consumers (event %s)." % event.get("event_id")
            )
        return True
