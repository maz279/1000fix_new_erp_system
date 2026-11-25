# S3 part 2 — the workstream itself: intake -> classification -> queue ->
# assignment, plus the routing features the first research pass omitted.
#
# The D365 pipeline this implements, in order:
#   1. INTAKE       a work item arrives from any source model (a conversation,
#                   a complaint, an AI handoff, a marketing-generated lead).
#   2. CLASSIFY     rulesets run in order; the first match sets priority,
#                   required skill, target queue, and may APPEND a capacity
#                   profile to the workstream default.
#   3. QUEUE        the item lands in a queue, with overflow and
#                   closure/unstaffed handling applied.
#   4. ASSIGN       push (presence- and capacity-gated), pick (the agent
#                   pulls) or bullseye (the eligible pool widens in rings).
#
# Three notes on judgment calls:
#
# PICK IS BUILT FIRST-CLASS, not as an afterthought, because it needs no
# presence model at all. The gap plan treats routing as one large build gated
# behind the hardest component; Microsoft ships pull as a peer of push, so a
# real slice of routing works here even where presence is not yet deployed.
#
# PREFERRED-AGENT AFFINITY reads fix.conversation history, which the estate
# has held all along. "Route to the expert who served this customer last" was
# listed as missing when the data to do it was already there.
#
# CAPACITY IS RELEASED BY WORK TYPE and never on a blanket rule. A record or
# activity work item does not release automatically at all, which looks like
# a bug until you read why: those work types have no end event, so releasing
# them on a guess would hand an agent capacity they are still using.

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_cc_routing import (
    ASSIGNMENT_METHODS,
    CHANNELS,
    WORK_TYPES,
)


class FixRoutingWorkstream(models.Model):
    """One intake pipeline. Owned by M27 and consumed by M34 and M32."""

    _name = "fix.routing.workstream"
    _description = "Routing Workstream"
    _order = "sequence, name"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    channel = fields.Selection(CHANNELS, required=True, default="voice")
    work_type = fields.Selection(
        WORK_TYPES,
        required=True,
        default="conversation",
        help="Determines the capacity RELEASE rule, which differs per type "
        "and is not a cosmetic label.",
    )
    source_model = fields.Char(
        help="The model this workstream routes, e.g. fix.conversation or "
        "fix.complaint. Informational: a workstream may route several.",
    )
    queue_id = fields.Many2one(
        "fix.cc.queue",
        string="Default Queue",
        required=True,
        help="Where a work item lands when no classification rule redirects it.",
    )
    default_capacity_profile_id = fields.Many2one(
        "fix.cc.capacity.profile",
        string="Default Capacity Profile",
        help="The workstream default. Microsoft's documented pattern is a "
        "Total-capacity profile here, with per-priority profiles appended by "
        "classification rules.",
    )
    use_capacity_units = fields.Boolean(
        string="Use Flat Units Instead of Profiles",
        default=False,
        help="The legacy flat max_agent_concurrency behaviour. Microsoft "
        "warns to configure profiles OR units and never both; the constraint "
        "below enforces that.",
    )
    assignment_method = fields.Selection(ASSIGNMENT_METHODS, required=True, default="pick")
    allowed_presence_ids = fields.Many2many(
        "fix.cc.presence.status",
        string="Allowed Presences",
        help="Which presence statuses may receive work from this workstream. "
        "Empty means every available-class status.",
    )
    prefer_last_agent = fields.Boolean(
        string="Prefer the Agent Who Served Last",
        default=False,
        help="Route to the representative who last handled this customer, if "
        "they are eligible. The history is already in fix.conversation.",
    )
    prefer_last_agent_days = fields.Integer(
        string="Affinity Lookback (days)",
        default=30,
        help="How far back to look for a previous handler. Beyond this the "
        "affinity is stale and ordinary routing applies.",
    )
    bullseye_ring_ids = fields.One2many(
        "fix.routing.bullseye.ring", "workstream_id", string="Bullseye Rings"
    )
    ruleset_ids = fields.One2many(
        "fix.routing.ruleset", "workstream_id", string="Classification Rules"
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )

    _code_unique = models.Constraint("UNIQUE (code)", "Each workstream code exists once.")

    @api.constrains("use_capacity_units", "default_capacity_profile_id")
    def _check_profiles_or_units_not_both(self):
        """Microsoft's own warning, enforced rather than documented.

        Configuring both means two different limits apply to the same agent
        and which one wins depends on the order the router happens to check
        them in. That is not a configuration anyone intends.
        """
        for rec in self:
            if rec.use_capacity_units and rec.default_capacity_profile_id:
                raise ValidationError(
                    "Workstream '%s' is set to use flat capacity units AND a "
                    "capacity profile. Configure one or the other — with both, "
                    "which limit applies depends on evaluation order." % rec.name
                )

    @api.constrains("assignment_method", "bullseye_ring_ids")
    def _check_bullseye_has_rings(self):
        for rec in self:
            if rec.assignment_method == "bullseye" and not rec.bullseye_ring_ids:
                raise ValidationError(
                    "Bullseye routing on '%s' defines no rings, so the eligible "
                    "pool would never widen. Add at least one ring." % rec.name
                )

    # ------------------------------------------------------------------
    # 1-2. Intake and classification
    # ------------------------------------------------------------------
    @api.model
    def for_conversation(self, conversation):
        """The workstream that routes this contact: its channel first.

        A workstream for the conversation's own channel wins; otherwise any
        workstream declared for fix.conversation. Empty when none exists, and
        the caller records why the contact is unrouted (A03 audit M27 G7).
        """
        base = [
            ("active", "=", True),
            ("company_id", "in", [conversation.company_id.id, False]),
            ("source_model", "in", [False, "", "fix.conversation"]),
        ]
        found = self.search([*base, ("channel", "=", conversation.channel)], limit=1)
        if not found:
            found = self.search(
                [
                    ("active", "=", True),
                    ("company_id", "in", [conversation.company_id.id, False]),
                    ("source_model", "=", "fix.conversation"),
                ],
                limit=1,
            )
        return found

    def intake(self, source_model, source_id, partner=None, context_values=None):
        """Create and classify a work item. The single entry to routing."""
        self.ensure_one()
        values = context_values or {}
        item = (
            self.env["fix.routing.workitem"]
            .sudo()
            .create(
                {
                    "workstream_id": self.id,
                    "source_model": source_model,
                    "source_id": source_id,
                    "partner_id": getattr(partner, "id", partner) or False,
                    "queue_id": self.queue_id.id,
                    "work_type": self.work_type,
                    "company_id": self.company_id.id,
                }
            )
        )
        item._classify(values)
        publish(
            self.env,
            "routing.work_item_created",
            "fix.routing.workitem",
            item.id,
            {
                "workstream": self.code,
                "source_model": source_model,
                "source_id": source_id,
                "queue": item.queue_id.code,
                "priority": item.priority,
                "skill": item.required_skill or None,
            },
        )
        return item

    def eligible_agents(self, item, ring=None):
        """Agents who could take this item, best first.

        The order of the filters is the order of cheapness: presence first (a
        cheap read), then capacity (a count per profile), then skill, then
        affinity. A different order would do the same work in more queries.
        """
        self.ensure_one()
        State = self.env["fix.cc.agent.state"].sudo()
        allowed = self.allowed_presence_ids
        domain = [("is_bookable", "=", True)]
        if allowed:
            domain.append(("presence_status_id", "in", allowed.ids))
        else:
            domain.append(("presence_status_id.is_available_class", "=", True))
        if ring is not None and ring.user_group_id:
            # Odoo 19 renamed res.users.groups_id; the old name crashed every
            # bullseye ring with a group (A03 audit M27 G10). all_group_ids
            # also counts groups held through implication.
            domain.append(("agent_id.all_group_ids", "in", ring.user_group_id.id))
        candidates = State.search(domain)
        candidates = candidates.filtered(lambda s: s.is_live())

        profiles = item.capacity_profile_ids
        if profiles:
            candidates = candidates.filtered(lambda s: s.has_capacity_for(profiles)[0])
        elif self.use_capacity_units:
            limit = self.queue_id.max_agent_concurrency or 1
            candidates = candidates.filtered(
                lambda s: self.env["fix.conversation"]
                .sudo()
                .search_count([("agent_id", "=", s.agent_id.id), ("state", "=", "with_agent")])
                < limit
            )

        if item.required_skill:
            skill = item.required_skill.strip().lower()
            candidates = candidates.filtered(
                lambda s: skill in (s.agent_id.cc_skills or "").lower()
            )

        if not candidates:
            return candidates

        preferred = item._preferred_agent() if self.prefer_last_agent else self.env["res.users"]
        ordered = candidates.sorted(
            key=lambda s: (
                0 if preferred and s.agent_id == preferred else 1,
                sum(s.units_held(p) for p in profiles) if profiles else 0,
                s.changed_at or fields.Datetime.now(),
            )
        )
        return ordered

    # ------------------------------------------------------------------
    # 4. Assignment
    # ------------------------------------------------------------------
    def assign_pending(self, limit=100):
        """Push or bullseye the pending items. Pick workstreams are skipped.

        A pick workstream has nothing to do here by design: its items wait in
        the queue until an agent claims one, which is the whole point and is
        why pick needs no presence model.
        """
        self.ensure_one()
        if self.assignment_method == "pick":
            return {"assigned": 0, "method": "pick", "note": "agents pull from the queue"}
        items = (
            self.env["fix.routing.workitem"]
            .sudo()
            .search(
                [
                    ("workstream_id", "=", self.id),
                    ("state", "=", "pending"),
                ],
                order="priority desc, created_at",
                limit=limit,
            )
        )
        assigned = 0
        for item in items:
            if item._offer_next():
                assigned += 1
        return {"assigned": assigned, "considered": len(items), "method": self.assignment_method}

    @api.model
    def cron_assign_pending(self, limit=200):
        total = {"assigned": 0, "considered": 0}
        for ws in self.sudo().search([("active", "=", True)]):
            result = ws.assign_pending(limit=limit)
            total["assigned"] += result.get("assigned", 0)
            total["considered"] += result.get("considered", 0)
        return total


class FixRoutingRuleset(models.Model):
    """A classification rule. First match wins, and may append a profile."""

    _name = "fix.routing.ruleset"
    _description = "Routing Classification Rule"
    _order = "workstream_id, sequence, id"

    workstream_id = fields.Many2one(
        "fix.routing.workstream", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(required=True, default=10)
    name = fields.Char(required=True)
    # --- condition (bounded, like the journey branch: no expression eval) ---
    condition_kind = fields.Selection(
        [
            ("always", "Always"),
            ("urgency", "Urgency level is at least"),
            ("channel", "Channel is"),
            ("intent", "Intent contains"),
            ("entitled", "Customer has a contract entitlement"),
            ("vip_tier", "Customer loyalty tier is at least"),
        ],
        required=True,
        default="always",
    )
    condition_value = fields.Char(
        help="The value the condition compares against; meaning depends on the " "condition kind."
    )
    # --- outcome ---
    target_queue_id = fields.Many2one(
        "fix.cc.queue", string="Route To Queue", help="Empty keeps the workstream default."
    )
    priority = fields.Integer(default=0, help="Higher is more urgent. Used to order the queue.")
    required_skill = fields.Char()
    appended_capacity_profile_id = fields.Many2one(
        "fix.cc.capacity.profile",
        string="Append Capacity Profile",
        help="Added to the workstream default for items this rule matches. "
        "Both profiles must have room for an agent to be eligible — this is "
        "the dual-profile mechanic, and it is the point of the field.",
    )
    stop_on_match = fields.Boolean(
        default=True,
        help="First-match-wins, as D365 does it. Turning this off lets later "
        "rules add further profiles to the same item.",
    )
    active = fields.Boolean(default=True)

    _sequence_unique = models.Constraint(
        "UNIQUE (workstream_id, sequence)",
        "Two classification rules of one workstream cannot share a sequence.",
    )

    def matches(self, item, values):
        """Evaluate this rule against a work item and its intake context."""
        self.ensure_one()
        kind = self.condition_kind
        if kind == "always":
            return True
        expected = (self.condition_value or "").strip()
        if kind == "channel":
            return self.workstream_id.channel == expected
        if kind == "urgency":
            order = ["low", "medium", "high", "critical"]
            actual = (values.get("urgency_level") or "medium").lower()
            if expected.lower() not in order or actual not in order:
                return False
            return order.index(actual) >= order.index(expected.lower())
        if kind == "intent":
            return expected.lower() in (values.get("intent") or "").lower()
        if kind == "entitled":
            if not item.partner_id:
                return False
            return bool(
                self.env["fix.routing.workitem"]._entitlement_summary(item.partner_id)[
                    "has_entitlement"
                ]
            )
        if kind == "vip_tier":
            if not item.partner_id or "fix.loyalty.account" not in self.env:
                return False
            account = (
                self.env["fix.loyalty.account"]
                .sudo()
                .search([("partner_id", "=", item.partner_id.id)], limit=1)
            )
            if not account or not account.tier_id:
                return False
            return (account.tier_id.name or "").strip().lower() == expected.lower()
        return False


class FixRoutingBullseyeRing(models.Model):
    """One ring of a bullseye: widen the eligible pool after a wait."""

    _name = "fix.routing.bullseye.ring"
    _description = "Bullseye Routing Ring"
    _order = "workstream_id, sequence, id"

    workstream_id = fields.Many2one(
        "fix.routing.workstream", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(required=True, default=10)
    name = fields.Char(required=True)
    wait_seconds = fields.Integer(
        required=True,
        default=30,
        help="How long to try this ring before widening to the next.",
    )
    user_group_id = fields.Many2one(
        "res.groups",
        string="User Group",
        help="The pool this ring opens. Empty means every eligible agent, "
        "which is what a final ring usually is.",
    )
    active = fields.Boolean(default=True)

    _sequence_unique = models.Constraint(
        "UNIQUE (workstream_id, sequence)",
        "Two rings of one workstream cannot share a sequence.",
    )

    @api.constrains("wait_seconds")
    def _check_wait(self):
        for rec in self:
            if rec.wait_seconds < 1:
                raise ValidationError(
                    "A bullseye ring must wait at least a second, or every ring "
                    "opens at once and the bullseye is just a flat pool."
                )
