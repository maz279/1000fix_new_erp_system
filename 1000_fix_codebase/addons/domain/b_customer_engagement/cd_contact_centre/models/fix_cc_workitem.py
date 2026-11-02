# S3 part 3 — the work item: the thing that is actually routed, assigned,
# held against capacity and released. Plus queue overflow and closure
# handling, the agent skill field routing needs, and WFM adherence.
#
# The capacity-release rules here are the part most worth reading twice,
# because they are not uniform and the estate's flat
# `max_agent_concurrency` had no notion of them at all:
#
#   conversation  releases when the rep ends it AND closes the session. Two
#                 events, not one -- a rep who hangs up but leaves the
#                 session open is still working it.
#   case          releases on resolve, on cancel, or when the owner is
#                 cleared.
#   record,       never release automatically. There is no end event to
#   activity      hang a release on, so releasing on a guess would hand the
#                 agent capacity they are still using. A supervisor releases
#                 these by hand, and that is the documented behaviour, not a
#                 shortfall.
#
# Capacity is also NOT consumed while merely monitoring a conversation, which
# is why `is_monitoring` exists and is excluded from every count.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

from .fix_cc_routing import WORK_TYPES, WORK_TYPES_WITHOUT_AUTO_RELEASE


class ResUsersCcSkills(models.Model):
    """The skill tags routing matches against.

    fix.cc.routing.rule has carried a free-text `skill` since it was written,
    and nothing anywhere recorded which agent HAS a skill -- so skill-based
    routing could never match. This is the missing half.
    """

    _inherit = "res.users"

    cc_skills = fields.Char(
        string="Contact Centre Skills",
        help="Comma-separated skill tags, e.g. 'laptop,printer,bengali'. "
        "Matched case-insensitively by the routing engine.",
    )

    def has_cc_skill(self, skill):
        self.ensure_one()
        if not skill:
            return True
        tags = {t.strip().lower() for t in (self.cc_skills or "").split(",") if t.strip()}
        return skill.strip().lower() in tags


class FixRoutingWorkitem(models.Model):
    """One unit of routed work, from intake to release."""

    _name = "fix.routing.workitem"
    _description = "Routing Work Item"
    _inherit = ["mail.thread"]
    _order = "priority desc, created_at, id"
    _rec_name = "display_label"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    workstream_id = fields.Many2one(
        "fix.routing.workstream", required=True, ondelete="cascade", index=True
    )
    queue_id = fields.Many2one("fix.cc.queue", required=True, index=True)
    work_type = fields.Selection(WORK_TYPES, required=True, default="conversation")
    source_model = fields.Char(required=True, index=True)
    source_id = fields.Integer(required=True, index=True)
    partner_id = fields.Many2one("res.partner", string="Customer", index=True)
    display_label = fields.Char(compute="_compute_display_label", store=True)

    priority = fields.Integer(default=0, index=True)
    required_skill = fields.Char()
    capacity_profile_ids = fields.Many2many(
        "fix.cc.capacity.profile",
        string="Capacity Profiles",
        help="The workstream default plus anything a classification rule "
        "appended. An agent needs room in EVERY one of these.",
    )
    classified_by_id = fields.Many2one("fix.routing.ruleset", string="Classified By", readonly=True)

    state = fields.Selection(
        [
            ("pending", "Pending assignment"),
            ("offered", "Offered to an agent"),
            ("assigned", "Assigned"),
            ("active", "Being worked"),
            ("closed", "Closed"),
            ("abandoned", "Abandoned"),
        ],
        required=True,
        default="pending",
        index=True,
        tracking=True,
    )
    assigned_agent_id = fields.Many2one("res.users", string="Assigned To", index=True)
    offered_agent_id = fields.Many2one("res.users", string="Offered To")
    offered_at = fields.Datetime(readonly=True)
    offer_expires_at = fields.Datetime(readonly=True)
    assignment_mode = fields.Selection(
        [
            ("push", "Pushed by the router"),
            ("pick", "Picked by the agent"),
            ("manual", "Assigned by a supervisor"),
            ("affinity", "Pushed to the previous handler"),
        ],
        readonly=True,
    )
    is_monitoring = fields.Boolean(
        string="Monitoring Only",
        default=False,
        help="A supervisor listening in. Monitoring does NOT consume capacity, "
        "which is Microsoft's rule and an easy one to get wrong.",
    )
    capacity_released = fields.Boolean(
        readonly=True,
        index=True,
        help="Whether this item has given its capacity back. Separate from "
        "'closed' because an end-of-day profile does not release on close.",
    )
    capacity_released_at = fields.Datetime(readonly=True)
    bullseye_ring_id = fields.Many2one(
        "fix.routing.bullseye.ring", string="Current Ring", readonly=True
    )
    created_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    assigned_at = fields.Datetime(readonly=True)
    closed_at = fields.Datetime(readonly=True)
    overflow_applied = fields.Char(
        readonly=True, help="Which overflow or closure action was taken, if any."
    )
    entitlement_note = fields.Char(
        readonly=True,
        help="The S5 entitlement verdict captured at intake, so the agent sees "
        "what the customer is contractually owed without a second lookup.",
    )

    @api.depends("source_model", "source_id", "partner_id")
    def _compute_display_label(self):
        # The model's own description ("Conversation #10"), not its technical
        # name: the label is what an agent reads in the queue.
        Model = self.env["ir.model"].sudo()
        for rec in self:
            who = rec.partner_id.name or "unidentified"
            kind = (
                (rec.source_model and Model._get(rec.source_model).name) or rec.source_model or "?"
            )
            rec.display_label = "%s #%s · %s" % (kind, rec.source_id or 0, who)

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------
    def _classify(self, values=None):
        """Run the workstream's rules in order. First match wins by default."""
        self.ensure_one()
        values = values or {}
        ws = self.workstream_id
        profiles = ws.default_capacity_profile_id
        vals = {
            "priority": 0,
            "required_skill": False,
            "queue_id": ws.queue_id.id,
            "classified_by_id": False,
        }
        appended = self.env["fix.cc.capacity.profile"]
        for rule in ws.ruleset_ids.filtered("active").sorted(lambda r: (r.sequence, r.id)):
            if not rule.matches(self, values):
                continue
            vals["classified_by_id"] = rule.id
            if rule.target_queue_id:
                vals["queue_id"] = rule.target_queue_id.id
            if rule.priority:
                vals["priority"] = rule.priority
            if rule.required_skill:
                vals["required_skill"] = rule.required_skill
            if rule.appended_capacity_profile_id:
                appended |= rule.appended_capacity_profile_id
            if rule.stop_on_match:
                break
        all_profiles = profiles | appended
        vals["capacity_profile_ids"] = [(6, 0, all_profiles.ids)]
        if self.partner_id:
            summary = self._entitlement_summary(self.partner_id)
            vals["entitlement_note"] = summary["note"]
        self.write(vals)
        self._apply_queue_conditions()
        return self

    # ------------------------------------------------------------------
    # S5 — entitlement lookup at intake
    # ------------------------------------------------------------------
    @api.model
    def _entitlement_summary(self, partner):
        """What is this customer contractually owed? (gap-plan service S5.)

        The entitlement model is M08's (fix.contract.entitlement in
        cd_contract_core) and the API lives there, where the data is owned.
        This is a SOFT lookup on purpose: making M27 hard-depend on the whole
        commercial contract stack — product, esignature, device registry — to
        read one number would couple the contact centre to half the estate
        for a label on a screen. When M08 is not installed the verdict says
        so rather than claiming the customer has nothing.
        """
        Entitlement = self.env.get("fix.contract.entitlement")
        if Entitlement is None:
            return {
                "has_entitlement": False,
                "available": False,
                "note": "Contract entitlements are not installed in this "
                "database, so none could be checked.",
                "lines": [],
            }
        return Entitlement.sudo().entitlement_summary_for_party(partner)

    # ------------------------------------------------------------------
    # Queue overflow and closure
    # ------------------------------------------------------------------
    def _apply_queue_conditions(self):
        """Overflow when the queue is swamped; divert when it is shut.

        The after-hours case is a live 16743 exposure: before this, a contact
        arriving at 02:00 joined a queue nobody was staffing and waited for a
        router that would never find an agent.
        """
        self.ensure_one()
        queue = self.queue_id
        action = queue.current_diversion()
        if not action:
            return False
        if action["action"] == "divert" and action["queue"]:
            self.write(
                {
                    "queue_id": action["queue"].id,
                    "overflow_applied": action["reason"],
                }
            )
        else:
            self.write({"overflow_applied": action["reason"]})
        publish(
            self.env,
            "routing.queue_diverted",
            "fix.routing.workitem",
            self.id,
            {
                "from_queue": queue.code,
                "to_queue": action["queue"].code if action["queue"] else None,
                "action": action["action"],
                "reason": action["reason"],
            },
        )
        return True

    # ------------------------------------------------------------------
    # Assignment: push, bullseye, pick, manual
    # ------------------------------------------------------------------
    def _preferred_agent(self):
        """The agent who last served this customer, within the lookback.

        Affinity reads conversation history, which has been in the estate all
        along — this capability was listed as missing while its data sat
        ready.
        """
        self.ensure_one()
        ws = self.workstream_id
        if not (ws.prefer_last_agent and self.partner_id):
            return self.env["res.users"]
        since = fields.Datetime.now() - timedelta(days=ws.prefer_last_agent_days or 30)
        previous = (
            self.env["fix.conversation"]
            .sudo()
            .search(
                [
                    ("customer_id", "=", self.partner_id.id),
                    ("agent_id", "!=", False),
                    ("started_at", ">=", since),
                ],
                order="started_at desc",
                limit=1,
            )
        )
        return previous.agent_id

    def _offer_next(self):
        """Offer this item to the next eligible agent (push or bullseye)."""
        self.ensure_one()
        ws = self.workstream_id
        ring = None
        if ws.assignment_method == "bullseye":
            ring = self._current_ring()
            if ring is None:
                return False
        agents = ws.eligible_agents(self, ring=ring)
        if not agents:
            return False
        state = agents[0]
        preferred = self._preferred_agent()
        self.write(
            {
                "state": "offered",
                "offered_agent_id": state.agent_id.id,
                "offered_at": fields.Datetime.now(),
                "offer_expires_at": fields.Datetime.add(
                    fields.Datetime.now(),
                    seconds=(ring.wait_seconds if ring else 30),
                ),
                "bullseye_ring_id": ring.id if ring else False,
                "assignment_mode": "affinity"
                if preferred and state.agent_id == preferred
                else "push",
            }
        )
        publish(
            self.env,
            "routing.work_item_offered",
            "fix.routing.workitem",
            self.id,
            {
                "agent_id": state.agent_id.id,
                "agent": state.agent_id.name,
                "queue": self.queue_id.code,
                "ring": ring.name if ring else None,
                "mode": self.assignment_mode,
            },
        )
        return True

    def _current_ring(self):
        """Which bullseye ring applies, given how long this item has waited."""
        self.ensure_one()
        rings = self.workstream_id.bullseye_ring_ids.filtered("active").sorted(
            lambda r: (r.sequence, r.id)
        )
        if not rings:
            return None
        waited = (fields.Datetime.now() - self.created_at).total_seconds()
        elapsed = 0
        for ring in rings:
            elapsed += ring.wait_seconds
            if waited <= elapsed:
                return ring
        # Past every ring: stay on the widest rather than stopping, because an
        # item that has outlasted the bullseye still needs somebody.
        return rings[-1]

    def action_accept(self):
        """The offered agent accepts. Capacity is consumed here, not at offer."""
        for item in self:
            if item.state != "offered":
                raise UserError("Only an offered work item can be accepted.")
            if item.offered_agent_id != self.env.user:
                raise UserError("This work item was offered to %s." % item.offered_agent_id.name)
            item._assign_to(self.env.user, mode=item.assignment_mode or "push")
        return True

    def action_reject(self, reason=""):
        """The offered agent declines, or the offer timed out.

        Rejection costs the agent their available status after the threshold,
        which is the mechanic D365 shipped in May 2026 for the obvious
        reason: an unresponsive agent marked available drains the queue one
        timeout at a time.
        """
        State = self.env["fix.cc.agent.state"].sudo()
        for item in self:
            if item.state != "offered":
                continue
            agent = item.offered_agent_id
            item.write(
                {
                    "state": "pending",
                    "offered_agent_id": False,
                    "offered_at": False,
                    "offer_expires_at": False,
                }
            )
            if agent:
                State.state_for(agent).register_missed_offer()
            publish(
                self.env,
                "routing.work_item_rejected",
                "fix.routing.workitem",
                item.id,
                {
                    "agent_id": agent.id if agent else None,
                    "reason": reason or "declined or timed out",
                    "queue": item.queue_id.code,
                },
            )
        return True

    def action_pick(self):
        """An agent pulls this item from the queue themselves.

        PICK, the assignment method that needs no presence engine. Capacity is
        still counted and may go NEGATIVE, because Microsoft documents exactly
        that for a manual pick and an arithmetic that clamps would hide a real
        overload from the supervisor looking at it.
        """
        for item in self:
            if item.state not in ("pending", "offered"):
                raise UserError(
                    "Only a queued work item can be picked (this one is %s)." % item.state
                )
            item._assign_to(self.env.user, mode="pick", enforce_capacity=False)
        return True

    def action_assign_manually(self, agent=None, reason=""):
        """A supervisor assigns, overriding capacity and presence.

        Microsoft's MC1173913: a manual assign updates capacity AND presence
        and stamps the owner. All three happen here, and the override is
        recorded with its reason rather than looking like ordinary routing.
        """
        agent_rec = agent if hasattr(agent, "id") else self.env["res.users"].browse(agent)
        if not agent_rec or not agent_rec.exists():
            raise UserError("Manual assignment needs the agent to assign to.")
        if not (reason or "").strip():
            raise UserError(
                "A manual assignment overrides the capacity and presence rules, "
                "so it requires a stated reason."
            )
        for item in self:
            item._assign_to(agent_rec, mode="manual", enforce_capacity=False)
            item.message_post(
                body="Assigned manually to %s by %s, overriding routing. Reason: %s"
                % (agent_rec.name, self.env.user.name, reason)
            )
        return True

    def _assign_to(self, agent, mode="push", enforce_capacity=True):
        self.ensure_one()
        State = self.env["fix.cc.agent.state"].sudo()
        state = State.state_for(agent)
        if enforce_capacity and self.capacity_profile_ids:
            ok, blocking = state.has_capacity_for(self.capacity_profile_ids)
            if not ok:
                raise UserError(
                    "%s has no free capacity against profile '%s' (%d of %d "
                    "held). Routing will offer this item to someone else."
                    % (
                        agent.name,
                        blocking.name,
                        state.units_held(blocking),
                        blocking.limit_for(agent),
                    )
                )
        self.write(
            {
                "state": "assigned",
                "assigned_agent_id": agent.id,
                "assigned_at": fields.Datetime.now(),
                "offered_agent_id": False,
                "offer_expires_at": False,
                "assignment_mode": mode,
            }
        )
        state.register_accepted_offer()
        # Presence is derived from capacity: taking this item may be what
        # fills a blocking profile and forces Busy-DND.
        state.enforce_capacity_blocking(self.capacity_profile_ids)
        publish(
            self.env,
            "routing.work_item_assigned",
            "fix.routing.workitem",
            self.id,
            {
                "agent_id": agent.id,
                "agent": agent.name,
                "queue": self.queue_id.code,
                "mode": mode,
                "profiles": self.capacity_profile_ids.mapped("code"),
            },
        )
        return True

    def action_start_work(self):
        for item in self:
            if item.state != "assigned":
                raise UserError("Only an assigned item can be started.")
            item.state = "active"
        return True

    # ------------------------------------------------------------------
    # Release — the per-work-type rules
    # ------------------------------------------------------------------
    def close_and_release(self, session_closed=False, reason=""):
        """Close the item and release capacity IF its work type allows.

        `session_closed` matters only for conversations, where Microsoft
        requires BOTH the conversation ending and the session closing. A rep
        who ends the call but leaves the session open is still working it, and
        giving the capacity back then would over-assign them.
        """
        for item in self:
            if item.state == "closed":
                continue
            releases = item._release_allowed(session_closed=session_closed)
            vals = {"state": "closed", "closed_at": fields.Datetime.now()}
            if releases:
                vals.update(
                    capacity_released=True,
                    capacity_released_at=fields.Datetime.now(),
                )
            item.write(vals)
            if not releases:
                item.message_post(
                    body="Closed without releasing capacity: %s"
                    % item._release_refusal_reason(session_closed)
                )
            publish(
                self.env,
                "routing.work_item_closed",
                "fix.routing.workitem",
                item.id,
                {
                    "queue": item.queue_id.code,
                    "work_type": item.work_type,
                    "capacity_released": releases,
                    "reason": reason or "",
                },
            )
            if item.assigned_agent_id:
                state = self.env["fix.cc.agent.state"].sudo().state_for(item.assigned_agent_id)
                state.enforce_capacity_blocking(item.capacity_profile_ids)
        return True

    def _release_allowed(self, session_closed=False):
        self.ensure_one()
        if self.is_monitoring:
            return True  # monitoring never consumed capacity to begin with
        if self.work_type in WORK_TYPES_WITHOUT_AUTO_RELEASE:
            return False
        if self.work_type == "conversation" and not session_closed:
            return False
        # An end-of-day profile does not give capacity back when an item
        # closes; that is what makes it a daily quota rather than a
        # concurrency limit.
        return not any(p.reset_frequency == "end_of_day" for p in self.capacity_profile_ids)

    def _release_refusal_reason(self, session_closed):
        self.ensure_one()
        if self.work_type in WORK_TYPES_WITHOUT_AUTO_RELEASE:
            return (
                "a %s work item has no end event, so capacity is released by a "
                "supervisor rather than guessed" % self.work_type
            )
        if self.work_type == "conversation" and not session_closed:
            return "the conversation ended but the agent's session is still open"
        if any(p.reset_frequency == "end_of_day" for p in self.capacity_profile_ids):
            return "an end-of-day capacity profile releases at the daily reset"
        return "release conditions not met"

    def action_release_capacity(self, reason=""):
        """A supervisor hands capacity back by hand."""
        if not (reason or "").strip():
            raise UserError("Releasing capacity by hand requires a stated reason.")
        for item in self:
            if item.capacity_released:
                continue
            item.write(
                {
                    "capacity_released": True,
                    "capacity_released_at": fields.Datetime.now(),
                }
            )
            item.message_post(
                body="Capacity released manually by %s. Reason: %s" % (self.env.user.name, reason)
            )
            if item.assigned_agent_id:
                self.env["fix.cc.agent.state"].sudo().state_for(
                    item.assigned_agent_id
                ).enforce_capacity_blocking(item.capacity_profile_ids)
        return True

    @api.model
    def cron_reset_end_of_day_capacity(self):
        """The daily reset an end-of-day profile waits for."""
        items = self.sudo().search(
            [
                ("state", "=", "closed"),
                ("capacity_released", "=", False),
                ("capacity_profile_ids.reset_frequency", "=", "end_of_day"),
            ]
        )
        items.write({"capacity_released": True, "capacity_released_at": fields.Datetime.now()})
        for agent in items.mapped("assigned_agent_id"):
            self.env["fix.cc.agent.state"].sudo().state_for(agent).enforce_capacity_blocking(
                items.filtered(lambda i, a=agent: i.assigned_agent_id == a).mapped(
                    "capacity_profile_ids"
                )
            )
        return len(items)

    @api.model
    def cron_expire_offers(self):
        """Take back offers nobody answered, and re-route them."""
        stale = self.sudo().search(
            [
                ("state", "=", "offered"),
                ("offer_expires_at", "!=", False),
                ("offer_expires_at", "<=", fields.Datetime.now()),
            ]
        )
        for item in stale:
            item.action_reject(reason="offer expired without an answer")
        return len(stale)
