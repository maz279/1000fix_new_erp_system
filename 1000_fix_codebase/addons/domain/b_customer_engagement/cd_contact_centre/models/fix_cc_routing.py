# S3 + S4 — Unified routing workstreams, capacity profiles and agent presence
# (A03 gap-plan Part IV, services S3 and S4).
#
# WHAT WAS HERE BEFORE. fix.cc.routing.rule held a priority, a channel and a
# free-text skill, and fix.cc.queue held a single flat `max_agent_concurrency`
# integer. get_available_agent() walked the first ten non-share users and
# handed the work to whoever had fewer than that many open conversations.
# There was no presence, no classification, no work type and no release rule.
#
# WHAT MICROSOFT ACTUALLY DOES, re-researched against Microsoft Learn in
# November 2026 because the first pass had recorded it as "per-channel unit
# profiles", which is not what it is. The specifics below are the reason this
# file is as long as it is; every one of them changes the data model:
#
#   * A capacity profile is FOUR fields: name, work-item limit, reset
#     frequency (Immediate or End of day), and assignment blocking.
#   * When the limit is reached with blocking on, the representative's
#     presence is FORCED to Busy-DND. Presence is therefore DERIVED from
#     capacity, not merely self-set — which is why S3 and S4 are one file.
#   * TWO profiles apply to each work item: the workstream default plus any
#     profile a classification ruleset APPENDS. A representative is eligible
#     only with free capacity in BOTH. The documented pattern is a
#     Total-capacity default plus per-priority appended profiles.
#   * Per-person overrides exist (msdyn_maxunits) and apply to NEW
#     assignments only; they do not retroactively change work already held.
#   * Capacity release DIFFERS BY WORK TYPE: a conversation releases when the
#     rep ends it and closes the session; a case on resolve/cancel or when
#     Worked By is cleared; records and activities NEVER release
#     automatically.
#   * Microsoft warns: configure profiles OR units, never both.
#   * Capacity may legitimately go NEGATIVE on a manual pick or forced
#     assign, so the arithmetic must not clamp at zero and pretend.
#   * Capacity is NOT consumed while merely monitoring a conversation.
#
# Also built here, from the routing features the first research pass omitted
# entirely: pick-based assignment (which needs no presence model at all and is
# therefore the cheapest real slice of S3), bullseye rings over user groups,
# overflow actions, queue-closure handling, preferred-agent affinity, and
# wait-time prediction off the Erlang-C engine that already existed.
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

_logger = logging.getLogger(__name__)

CHANNELS = [
    ("voice", "Voice (hotline 16743)"),
    ("whatsapp", "WhatsApp"),
    ("chat", "Web Chat"),
    ("email", "E-mail"),
    ("in_app", "In-App"),
]

# The work types, each with its own capacity-release rule. The rules are
# Microsoft's, and they are genuinely different from one another -- treating
# them alike is how an estate ends up with capacity that never comes back.
WORK_TYPES = [
    ("conversation", "Conversation (releases when ended and the session closes)"),
    ("case", "Case (releases on resolve, cancel, or clearing the owner)"),
    ("record", "Record (never releases automatically)"),
    ("activity", "Activity (never releases automatically)"),
]
WORK_TYPES_WITHOUT_AUTO_RELEASE = {"record", "activity"}

ASSIGNMENT_METHODS = [
    ("push", "Push — route to the most available eligible representative"),
    ("pick", "Pick — representatives pull from the queue themselves"),
    ("bullseye", "Bullseye — widen the eligible pool in timed rings"),
]


class FixCcPresenceStatus(models.Model):
    """A presence status, as configurable data rather than a hard-coded list.

    Microsoft models presence as records precisely so that a tenant can add
    "On training" or "In a huddle" without a code change, and so that the
    rule "only available-class statuses receive work" can be a property of
    the status instead of a magic string comparison somewhere in the router.
    """

    _name = "fix.cc.presence.status"
    _description = "Agent Presence Status"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    is_available_class = fields.Boolean(
        string="Receives Work",
        default=False,
        help="Only an available-class status is eligible for routed work. "
        "This is the single place that rule is expressed.",
    )
    is_system_dnd = fields.Boolean(
        string="System Busy-DND",
        default=False,
        help="The status capacity blocking forces an agent into. Exactly one "
        "status should carry this.",
    )
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("UNIQUE (code)", "Each presence code exists once.")

    @api.constrains("is_available_class", "is_system_dnd")
    def _check_dnd_is_not_available(self):
        for rec in self:
            if rec.is_system_dnd and rec.is_available_class:
                raise ValidationError(
                    "Busy-DND is the status an agent is forced into when their "
                    "capacity blocks. It cannot also be a status that receives "
                    "work, or blocking would do nothing."
                )

    @api.model
    def dnd_status(self):
        return self.sudo().search([("is_system_dnd", "=", True)], limit=1)

    def action_set_my_presence(self):
        """FR-CCE-032: the signed-in agent sets their OWN presence to this status.

        Every set_presence() caller was system-forced (capacity blocking, a
        missed offer, the capacity release), so no agent could ever make
        themselves available and the routing pool could only be filled by a
        script. This goes through set_presence(), so the change is logged
        with source "manual" and adherence is measured from it; an agent
        with no presence row yet gets one (offline first, then this status).
        """
        self.ensure_one()
        if not self.active:
            raise UserError("Presence %s is retired and cannot be chosen." % self.name)
        state = self.env["fix.cc.agent.state"].state_for(self.env.user)
        state.set_presence(self, source="manual")
        return True


class FixCcCapacityProfile(models.Model):
    """A capacity profile — the four fields Microsoft defines, and no more."""

    _name = "fix.cc.capacity.profile"
    _description = "Capacity Profile"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    work_item_limit = fields.Integer(
        required=True,
        default=1,
        help="How many work items an agent may hold against this profile.",
    )
    reset_frequency = fields.Selection(
        [
            ("immediate", "Immediate — capacity returns as each item closes"),
            ("end_of_day", "End of day — capacity returns at the daily reset"),
        ],
        required=True,
        default="immediate",
        help="An end-of-day profile is how a daily quota is modelled: closing "
        "an item does NOT give the capacity back.",
    )
    assignment_blocking = fields.Boolean(
        string="Assignment Blocking",
        default=True,
        help="When the limit is reached, force the agent's presence to "
        "Busy-DND so no further work is offered. With blocking off the limit "
        "is advisory and the router may exceed it.",
    )
    assignment_ids = fields.One2many(
        "fix.cc.capacity.assignment",
        "profile_id",
        string="Agents On This Profile",
        help="Who holds this profile, and whether they have a personal limit.",
    )
    agent_count = fields.Integer(compute="_compute_agent_count", string="Agents")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    _code_unique = models.Constraint("UNIQUE (code)", "Each capacity profile code exists once.")

    @api.depends("assignment_ids.active")
    def _compute_agent_count(self):
        for rec in self:
            rec.agent_count = len(rec.assignment_ids.filtered("active"))

    @api.constrains("work_item_limit")
    def _check_limit(self):
        for rec in self:
            if rec.work_item_limit < 1:
                raise ValidationError(
                    "A capacity profile must allow at least one work item. To "
                    "stop routing to someone, change their presence."
                )

    def limit_for(self, agent):
        """The limit in force for this agent, honouring a personal override.

        Microsoft's msdyn_maxunits equivalent. The override applies to NEW
        assignments only, which falls out naturally: this is consulted at
        assignment time and never rewrites work already held.
        """
        self.ensure_one()
        override = (
            self.env["fix.cc.capacity.assignment"]
            .sudo()
            .search(
                [
                    ("profile_id", "=", self.id),
                    ("agent_id", "=", getattr(agent, "id", agent)),
                    ("active", "=", True),
                ],
                limit=1,
            )
        )
        if override and override.max_units_override:
            return override.max_units_override
        return self.work_item_limit


class FixCcCapacityAssignment(models.Model):
    """An agent's membership of a capacity profile, with an optional personal
    limit. The equivalent of msdyn_bookableresourcecapacityprofile."""

    _name = "fix.cc.capacity.assignment"
    _description = "Agent Capacity Profile Assignment"
    _order = "agent_id, profile_id"

    agent_id = fields.Many2one("res.users", required=True, index=True, ondelete="cascade")
    profile_id = fields.Many2one(
        "fix.cc.capacity.profile", required=True, index=True, ondelete="cascade"
    )
    max_units_override = fields.Integer(
        string="Personal Limit",
        help="Overrides the profile limit for this agent. 0 means use the "
        "profile's own limit. Applies to NEW assignments only.",
    )
    active = fields.Boolean(default=True)

    _agent_profile_unique = models.Constraint(
        "UNIQUE (agent_id, profile_id)",
        "An agent holds each capacity profile once.",
    )


class FixCcAgentState(models.Model):
    """Live agent presence — the S4 model the estate did not have.

    fix.cc.wfm.shift says who was SCHEDULED. This says who is actually there
    right now, which is a different question and the one routing needs.
    """

    _name = "fix.cc.agent.state"
    _description = "Agent Presence State"
    _order = "agent_id"
    _rec_name = "agent_id"

    agent_id = fields.Many2one(
        "res.users", required=True, index=True, ondelete="cascade", string="Agent"
    )
    presence_status_id = fields.Many2one(
        "fix.cc.presence.status",
        required=True,
        string="Presence",
        # No `tracking=True`: this model does not inherit mail.thread, so Odoo
        # ignores the parameter and warns at load. The authoritative trail is
        # fix.cc.agent.state.log, which set_presence() appends to on every
        # change and which adherence is computed from. Adding mail.thread here
        # would create a SECOND, partial history beside the real one.
    )
    presence_source = fields.Selection(
        [
            ("manual", "Set by the agent"),
            ("capacity_block", "Forced by a blocking capacity profile"),
            ("missed_notification", "Forced after a missed or rejected offer"),
            ("shift", "Set by the roster"),
            ("system", "Set by the system"),
        ],
        required=True,
        default="manual",
        help="Presence is not only self-set. Recording WHY it changed is what "
        "makes adherence and the missed-offer rule auditable.",
    )
    changed_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    heartbeat_at = fields.Datetime(
        help="Last sign of life from the agent's client. A stale heartbeat "
        "means the state is not trustworthy and the agent is treated as "
        "offline rather than silently drained of work."
    )
    is_bookable = fields.Boolean(
        string="Bookable Resource",
        default=True,
        help="Microsoft requires representatives to exist as bookable "
        "resources before unified routing will consider them.",
    )
    missed_offers = fields.Integer(
        default=0,
        readonly=True,
        help="Consecutive offers missed or rejected. Reset on an accept.",
    )
    log_ids = fields.One2many(
        "fix.cc.agent.state.log",
        "state_id",
        string="Presence History",
        help="The append-only interval history adherence is measured from.",
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )

    _agent_unique = models.Constraint("UNIQUE (agent_id)", "One live presence row per agent.")

    # How stale a heartbeat may be before the agent is treated as gone.
    HEARTBEAT_GRACE_MINUTES = 5

    @api.model
    def state_for(self, agent, create=True):
        """This agent's presence row, created offline-by-default if absent.

        Defaulting a missing row to an available status would quietly enrol
        every new user into the routing pool, so the default is offline.
        """
        agent_id = getattr(agent, "id", agent)
        row = self.sudo().search([("agent_id", "=", agent_id)], limit=1)
        if row or not create:
            return row
        offline = (
            self.env["fix.cc.presence.status"]
            .sudo()
            .search(
                [("is_available_class", "=", False), ("is_system_dnd", "=", False)],
                order="sequence",
                limit=1,
            )
        )
        if not offline:
            raise UserError(
                "No presence statuses are configured, so agent presence cannot "
                "be tracked. Load the presence status data before routing."
            )
        return self.sudo().create(
            {
                "agent_id": agent_id,
                "presence_status_id": offline.id,
                "presence_source": "system",
            }
        )

    def set_presence(self, status, source="manual"):
        """Change presence, recording why, and log the transition.

        The log is what adherence is computed from, so every change goes
        through here rather than writing the field directly.
        """
        status_rec = (
            status
            if hasattr(status, "id")
            else (
                self.env["fix.cc.presence.status"].sudo().search([("code", "=", status)], limit=1)
            )
        )
        if not status_rec:
            raise ValidationError("Unknown presence status %r." % status)
        Log = self.env["fix.cc.agent.state.log"].sudo()
        now = fields.Datetime.now()
        for rec in self:
            if rec.presence_status_id == status_rec and rec.presence_source == source:
                rec.heartbeat_at = now
                continue
            Log.close_open(rec.agent_id, now)
            rec.write(
                {
                    "presence_status_id": status_rec.id,
                    "presence_source": source,
                    "changed_at": now,
                    "heartbeat_at": now,
                }
            )
            Log.create(
                {
                    "agent_id": rec.agent_id.id,
                    "state_id": rec.id,
                    "presence_status_id": status_rec.id,
                    "presence_source": source,
                    "from_at": now,
                    "company_id": rec.company_id.id,
                }
            )
            publish(
                self.env,
                "agent.presence_changed",
                "fix.cc.agent.state",
                rec.id,
                {
                    "agent_id": rec.agent_id.id,
                    "agent": rec.agent_id.name,
                    "presence": status_rec.code,
                    "receives_work": status_rec.is_available_class,
                    "source": source,
                },
            )
        return True

    def heartbeat(self):
        for rec in self:
            rec.heartbeat_at = fields.Datetime.now()
        return True

    def is_live(self):
        """Is this presence row current enough to route against?"""
        self.ensure_one()
        if not self.heartbeat_at:
            # No client has ever checked in. A manually-set presence is still
            # honoured -- a supervisor marking someone available is a real
            # signal -- but a derived one is not.
            return self.presence_source in ("manual", "shift")
        age = fields.Datetime.now() - self.heartbeat_at
        return age <= timedelta(minutes=self.HEARTBEAT_GRACE_MINUTES)

    def register_missed_offer(self, threshold=2):
        """A missed or rejected offer costs the agent their available status.

        D365 shipped automatic presence update on missed/rejected
        notifications (GA 1 May 2026) for exactly one reason: an agent who is
        marked available but is not at their desk otherwise drains the queue
        one timeout at a time.
        """
        dnd = self.env["fix.cc.presence.status"].dnd_status()
        for rec in self:
            rec.missed_offers += 1
            if rec.missed_offers >= threshold and dnd:
                rec.set_presence(dnd, source="missed_notification")
                publish(
                    self.env,
                    "agent.forced_unavailable",
                    "fix.cc.agent.state",
                    rec.id,
                    {
                        "agent_id": rec.agent_id.id,
                        "agent": rec.agent_id.name,
                        "missed_offers": rec.missed_offers,
                        "threshold": threshold,
                    },
                )
        return True

    def register_accepted_offer(self):
        for rec in self:
            rec.missed_offers = 0
        return True

    # --- capacity --------------------------------------------------------
    def units_held(self, profile):
        """Work items this agent currently holds against one profile.

        Deliberately NOT clamped at zero. Microsoft documents that capacity
        can legitimately go negative after a manual pick or a forced assign,
        and a figure that hides that is worse than one that shows it.
        """
        self.ensure_one()
        return (
            self.env["fix.routing.workitem"]
            .sudo()
            .search_count(
                [
                    ("assigned_agent_id", "=", self.agent_id.id),
                    ("state", "in", ("assigned", "active")),
                    ("capacity_profile_ids", "in", profile.id),
                    ("capacity_released", "=", False),
                ]
            )
        )

    def has_capacity_for(self, profiles):
        """Free capacity in EVERY applicable profile, not just one.

        This is the mechanic the first research pass missed: the workstream
        default AND any classification-appended profile both have to have
        room. Returning the blocking profile lets the caller explain itself.
        """
        self.ensure_one()
        for profile in profiles:
            if self.units_held(profile) >= profile.limit_for(self.agent_id):
                return False, profile
        return True, None

    def enforce_capacity_blocking(self, profiles):
        """Force Busy-DND when a blocking profile is full; release when not.

        This is the derivation that makes presence a function of capacity
        rather than only of the agent's own choice.
        """
        self.ensure_one()
        dnd = self.env["fix.cc.presence.status"].dnd_status()
        if not dnd:
            return False
        blocked = False
        for profile in profiles:
            if not profile.assignment_blocking:
                continue
            if self.units_held(profile) >= profile.limit_for(self.agent_id):
                blocked = True
                break
        if blocked and self.presence_status_id != dnd:
            self.set_presence(dnd, source="capacity_block")
            return True
        if (
            not blocked
            and self.presence_status_id == dnd
            and self.presence_source == "capacity_block"
        ):
            # Only a capacity-forced DND is lifted automatically. A DND the
            # agent set themselves, or one a missed offer imposed, is theirs
            # to clear.
            available = (
                self.env["fix.cc.presence.status"]
                .sudo()
                .search([("is_available_class", "=", True)], order="sequence", limit=1)
            )
            if available:
                self.set_presence(available, source="system")
                return True
        return False


class FixCcAgentStateLog(models.Model):
    """Append-only presence history. The basis for adherence.

    Adherence is "scheduled versus actually present", and the estate had the
    roster and the Erlang-C forecast but nothing recording the second half.
    Without this table adherence can only be asserted.
    """

    _name = "fix.cc.agent.state.log"
    _description = "Agent Presence History"
    _order = "from_at desc, id desc"

    agent_id = fields.Many2one("res.users", required=True, index=True, ondelete="cascade")
    state_id = fields.Many2one(
        "fix.cc.agent.state",
        string="Presence Row",
        index=True,
        ondelete="cascade",
        help="The live presence row this interval belongs to. Carried as well "
        "as agent_id so the presence form can show its own history.",
    )
    presence_status_id = fields.Many2one(
        "fix.cc.presence.status", required=True, ondelete="restrict"
    )
    presence_source = fields.Selection(
        [
            ("manual", "Set by the agent"),
            ("capacity_block", "Forced by a blocking capacity profile"),
            ("missed_notification", "Forced after a missed or rejected offer"),
            ("shift", "Set by the roster"),
            ("system", "Set by the system"),
        ],
        required=True,
        default="manual",
    )
    from_at = fields.Datetime(required=True, index=True)
    to_at = fields.Datetime(index=True, help="Empty while this is the current state.")
    minutes = fields.Float(compute="_compute_minutes", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )

    @api.depends("from_at", "to_at")
    def _compute_minutes(self):
        now = fields.Datetime.now()
        for rec in self:
            end = rec.to_at or now
            rec.minutes = (end - rec.from_at).total_seconds() / 60.0 if rec.from_at else 0.0

    @api.depends("agent_id", "presence_status_id", "from_at")
    def _compute_display_name(self):
        """Without this a history row renders as "fix.cc.agent.state.log,13".

        That is what every many2one to this table showed, the presence form's
        own history grid included. A COMPUTE, not a stored related Char: the
        agent's name and the status name are translatable, and a stored copy
        freezes whichever language wrote it — which in a bilingual-by-mandate
        estate means a Bengali session reading a stale English label.
        """
        for rec in self:
            when = "—"
            if rec.from_at:
                local = fields.Datetime.context_timestamp(rec, rec.from_at)
                when = local.strftime("%d %b %H:%M")
            rec.display_name = "%s · %s · %s" % (
                rec.agent_id.display_name or "—",
                rec.presence_status_id.display_name or "—",
                when,
            )

    @api.model
    def close_open(self, agent, when=None):
        """Close the agent's currently-open interval."""
        open_rows = self.sudo().search(
            [("agent_id", "=", getattr(agent, "id", agent)), ("to_at", "=", False)]
        )
        if open_rows:
            open_rows.write({"to_at": when or fields.Datetime.now()})
        return open_rows

    def write(self, vals):
        """History is append-only apart from closing an open interval."""
        allowed = {"to_at", "minutes"}
        if set(vals) - allowed:
            for rec in self:
                if rec.to_at:
                    raise UserError(
                        "Presence history is append-only; a closed interval " "cannot be rewritten."
                    )
        return super().write(vals)

    def unlink(self):
        raise UserError("Presence history cannot be deleted — adherence is measured from it.")
