# M35 journey runtime — S10 applied to marketing journeys.
#
# WHAT WAS HERE BEFORE. fix.campaign.journey held a name, a free-text
# trigger_event and a steps_json blob, and nothing executed any of it. The
# screen let a marketer author a journey the estate would never run.
#
# THE DESIGN CONSTRAINT THAT SHAPED THIS FILE (November 2026 research against
# Microsoft Learn, recorded in the gap plan as a W1 item precisely because it
# is a schema decision and not a feature):
#
#   D365 journeys come in TWO KINDS with different membership semantics.
#   A SEGMENT-BASED journey starts on a schedule against an audience
#   definition and enumerates that audience at launch. A TRIGGER-BASED
#   journey starts immediately on a customer action and admits ONE member at
#   a time, so it must be idempotent per member per event.
#
#   The old single model conflated them. Building the executor without the
#   discriminator would have meant rebuilding the executor, which is why the
#   gap plan pulled it into W1 ahead of the rest of S10.
#
# The second research finding is enforced by the engine rather than here:
# Microsoft is shipping edit-and-republish of a segment already in use by a
# LIVE journey, with additions applied in real time. So no step may trust the
# launch-time snapshot — membership and consent are re-evaluated before every
# step (see _runtime_member_still_eligible below, called by the shared engine
# in cd_entity_config). Without that, a party who withdraws consent after
# step 1 still receives step 3.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_campaign import CONSENT_CHANNEL_FOR

# Which delivery channel a journey step may send on. These are S1's channels;
# the journey does not invent any of its own.
STEP_CHANNELS = [
    ("sms", "SMS"),
    ("whatsapp", "WhatsApp"),
    ("email", "E-mail"),
    ("push", "Push"),
]

STEP_TYPES = [
    ("send", "Send a message"),
    ("wait", "Wait"),
    ("branch", "Branch on a condition"),
    ("segment_add", "Add to a segment"),
    ("segment_remove", "Remove from a segment"),
    ("publish_event", "Publish an event for another module"),
    ("exit", "Exit the journey"),
]

# Fields a branch step may read on the party. A WHITELIST, deliberately:
# journeys are authored by marketers, and letting authored text name any
# field (or worse, evaluate an expression) would turn the journey designer
# into a way to read the whole party record, PII included.
BRANCH_PARTNER_FIELDS = {
    "party_status": "Party status",
    "preferred_language": "Preferred language",
    "country_id": "Country",
    "city": "City",
    "is_company": "Is a company",
}


class FixCampaignJourney(models.Model):
    """A journey that actually runs, in one of the two D365 kinds."""

    _name = "fix.campaign.journey"
    _inherit = ["fix.campaign.journey", "fix.step.runtime.mixin"]

    # --- the S10 engine contract ---
    _runtime_member_model = "fix.campaign.journey.member"
    _runtime_member_flow_field = "journey_id"

    journey_kind = fields.Selection(
        [
            ("segment_scheduled", "Segment-based (scheduled against an audience)"),
            ("trigger_immediate", "Trigger-based (immediate, on a customer action)"),
            ("campaign_audience", "Campaign audience (enrols the launch recipients)"),
        ],
        string="Journey Kind",
        required=True,
        default="trigger_immediate",
        help="D365 makes this distinction and so must we: a segment journey "
        "enumerates its audience at launch, a trigger journey admits one "
        "member per event and must be idempotent. The two cannot share one "
        "code path. A campaign-audience journey enrols the recipients the "
        "campaign launch resolved (consented and DND-scrubbed), and is how a "
        "launch starts sending.",
    )
    segment_id = fields.Many2one(
        "fix.segment",
        string="Audience Segment",
        help="Required for a segment-based journey. Membership resolves "
        "through M33 — a journey never defines its own audience.",
    )
    trigger_id = fields.Many2one(
        "fix.campaign.trigger",
        string="Starting Trigger",
        help="Required for a trigger-based journey.",
    )
    live_segment_sync = fields.Boolean(
        string="Apply Segment Changes Live",
        default=True,
        help="Admit parties who join the segment while this journey is "
        "running, and exit parties who leave it. D365 is shipping exactly "
        "this (segment republish into a live journey); with it off, the "
        "journey works from the launch-time snapshot only.",
    )
    exit_on_consent_withdrawal = fields.Boolean(
        string="Exit on Consent Withdrawal",
        default=True,
        help="Remove a party from the journey as soon as they withdraw "
        "marketing consent, rather than walking them to the next send and "
        "suppressing it there. The send would be suppressed either way; this "
        "stops spending steps on someone who has opted out.",
    )
    step_ids = fields.One2many("fix.campaign.journey.step", "journey_id", string="Steps", copy=True)
    member_ids = fields.One2many("fix.campaign.journey.member", "journey_id", string="Members")
    step_count = fields.Integer(compute="_compute_counts", string="Steps")
    member_active_count = fields.Integer(compute="_compute_counts", string="Active Members")
    member_completed_count = fields.Integer(compute="_compute_counts", string="Completed")
    member_exited_count = fields.Integer(compute="_compute_counts", string="Exited")
    launched_at = fields.Datetime(readonly=True, copy=False)

    @api.depends("step_ids", "member_ids.state")
    def _compute_counts(self):
        for rec in self:
            rec.step_count = len(rec.step_ids)
            rec.member_active_count = len(rec.member_ids.filtered(lambda m: m.state == "active"))
            rec.member_completed_count = len(
                rec.member_ids.filtered(lambda m: m.state == "completed")
            )
            rec.member_exited_count = len(
                rec.member_ids.filtered(lambda m: m.state in ("exited", "failed"))
            )

    @api.constrains("journey_kind", "segment_id", "trigger_id")
    def _check_kind_has_its_starter(self):
        """A journey kind without its starter cannot run, so it cannot save.

        This is the constraint the discriminator exists for: a segment
        journey with no segment and a trigger journey with no trigger are
        both authored journeys that would silently never enrol anybody.
        """
        for rec in self:
            if rec.journey_kind == "segment_scheduled" and not rec.segment_id:
                raise ValidationError(
                    "A segment-based journey needs its audience segment — "
                    "without one it would enrol nobody at launch."
                )
            if rec.journey_kind == "trigger_immediate" and not rec.trigger_id:
                raise ValidationError(
                    "A trigger-based journey needs its starting trigger — "
                    "without one nothing would ever admit a member."
                )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def action_activate(self):
        """Start the journey. For a segment kind this enrols the audience.

        The parent campaign must be running: a journey is how a campaign
        reaches people, so it cannot outrun the campaign's own budget DOFA
        and BTRC launch gates. Those gates are on fix.campaign and are not
        re-implemented here.
        """
        for rec in self:
            if rec.state == "active":
                raise UserError("This journey is already active.")
            if not rec.step_ids:
                raise UserError(
                    "A journey with no steps has nothing to do. Add at least "
                    "one step before activating."
                )
            if rec.campaign_id.state != "running":
                raise UserError(
                    "Campaign '%s' is %s. A journey only runs under a running "
                    "campaign, so that the campaign's budget approval and BTRC "
                    "launch gates apply to everything it sends."
                    % (rec.campaign_id.name, rec.campaign_id.state)
                )
            rec._guarded().write(
                {
                    "state": "active",
                    "launched_at": fields.Datetime.now(),
                    "paused_by_campaign": False,
                }
            )
            enrolled = 0
            if rec.journey_kind == "segment_scheduled":
                enrolled = rec._enrol_segment_members()
            elif rec.journey_kind == "campaign_audience":
                enrolled = rec._enrol(rec.campaign_id.recipient_ids, source="launch")
            publish(
                self.env,
                "journey.activated",
                "fix.campaign.journey",
                rec.id,
                {
                    "journey": rec.name,
                    "kind": rec.journey_kind,
                    "campaign": rec.campaign_id.name,
                    "steps": len(rec.step_ids),
                    "enrolled": enrolled,
                },
            )
        return True

    def action_pause_journey(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active journey can be paused.")
            rec._guarded().write({"state": "paused", "paused_by_campaign": False})
        return True

    def action_resume_journey(self):
        for rec in self:
            if rec.state != "paused":
                raise UserError("Only a paused journey can be resumed.")
            rec._assert_campaign_running()
            rec._guarded().write({"state": "active", "paused_by_campaign": False})
        return True

    def _assert_campaign_running(self):
        """A journey sends only while its campaign runs (A03 audit G-M35-5)."""
        self.ensure_one()
        if self.campaign_id.state != "running":
            raise UserError(
                "Campaign '%s' is %s. Resume the campaign: a journey cannot send "
                "for a campaign that is not running."
                % (self.campaign_id.name, self.campaign_id.state)
            )

    def _pause_for_campaign(self):
        """Called by fix.campaign.action_pause / action_complete."""
        self._guarded().write({"state": "paused", "paused_by_campaign": True})

    def _resume_for_campaign(self):
        """Called by fix.campaign.action_resume: only what the pause stopped."""
        self.filtered(lambda j: j.state == "paused")._guarded().write(
            {"state": "active", "paused_by_campaign": False}
        )

    # ------------------------------------------------------------------
    # Enrolment
    # ------------------------------------------------------------------
    def _enrol_segment_members(self):
        """Enrol the segment's current members. Idempotent by enrol_key."""
        self.ensure_one()
        if self.journey_kind != "segment_scheduled" or not self.segment_id:
            return 0
        partners = self.segment_id.membership_ids.filtered(lambda m: not m.exited_at).mapped(
            "partner_id"
        )
        return self._enrol(partners, source="launch")

    def _enrol(self, partners, source="launch", source_event_id=None):
        """Create members for these parties, skipping any already enrolled."""
        self.ensure_one()
        Member = self.env["fix.campaign.journey.member"].sudo()
        first = self._runtime_first_step()
        created = 0
        # BTRC DND (A03 audit G-M35-4): a listed party is never enrolled, on
        # any journey kind, so a segment or trigger journey cannot route
        # around the campaign's recipient scrub.
        for partner in self.campaign_id._dnd_reachable(partners):
            key = "%d:%d:%s" % (self.id, partner.id, source_event_id or source)
            if Member.search_count([("enrol_key", "=", key)]):
                continue
            Member.create(
                {
                    "journey_id": self.id,
                    "partner_id": partner.id,
                    "current_step_id": first.id if first else False,
                    "enrol_key": key,
                    "source_event_id": source_event_id or False,
                    "enrol_source": source,
                    "next_action_at": fields.Datetime.now(),
                    "company_id": self.campaign_id.company_id.id,
                }
            )
            created += 1
        return created

    @api.model
    def enrol_from_event(self, event):
        """Admit one member per trigger-based journey listening for this event.

        This is the trigger half of the kind discriminator. The event's own id
        is the idempotency key, so a replayed outbox event re-enrols nobody —
        which is the property a trigger journey needs and a segment journey
        does not.
        """
        event_type = (event or {}).get("event_type") or ""
        payload = (event or {}).get("payload") or {}
        partner_id = (
            payload.get("partner_id")
            or payload.get("customer_id")
            or (event.get("aggregate_id") if event.get("aggregate") == "res.partner" else None)
        )
        if not partner_id:
            return {"enrolled": 0, "reason": "event carries no party"}
        partner = self.env["res.partner"].browse(partner_id).exists()
        if not partner:
            return {"enrolled": 0, "reason": "party %s not found" % partner_id}

        journeys = self.sudo().search(
            [
                ("state", "=", "active"),
                ("campaign_id.state", "=", "running"),
                ("journey_kind", "=", "trigger_immediate"),
                ("trigger_id.active", "=", True),
                ("trigger_id.outbox_event_type", "=", event_type),
            ]
        )
        enrolled = 0
        for journey in journeys:
            delay = (journey.trigger_id.delay_hours or 0) * 60
            created = journey._enrol(
                partner, source="trigger", source_event_id=event.get("event_id")
            )
            if created and delay:
                members = (
                    self.env["fix.campaign.journey.member"]
                    .sudo()
                    .search(
                        [
                            ("journey_id", "=", journey.id),
                            ("partner_id", "=", partner.id),
                            ("source_event_id", "=", event.get("event_id")),
                        ]
                    )
                )
                members.write(
                    {"next_action_at": fields.Datetime.add(fields.Datetime.now(), minutes=delay)}
                )
            enrolled += created
        return {"enrolled": enrolled, "journeys": len(journeys)}

    @api.model
    def consume_journey_trigger(self, event):
        """R8 consumer for every trigger event type (data/fix_journey_consumers.xml).

        A03 audit G-M35-8: enrol_from_event had no caller, so no trigger
        journey ever admitted a member. Idempotent per (journey, party,
        event): the member's enrol_key carries the event id, so a redelivered
        event enrols nobody twice.
        """
        return self.enrol_from_event(event)

    # ------------------------------------------------------------------
    # The S10 contract
    # ------------------------------------------------------------------
    def _runtime_ordered_steps(self):
        self.ensure_one()
        return self.step_ids.filtered("active").sorted(lambda s: (s.sequence, s.id))

    def _runtime_current_step(self, member):
        return member.current_step_id

    def _runtime_set_step(self, member, step):
        member.sudo().write({"current_step_id": step.id if step else False})

    def _runtime_member_still_eligible(self, member):
        """Re-evaluated before EVERY step — see the file header.

        Two checks, both of which the launch-time snapshot cannot give you:
        is this party still in the audience, and have they withdrawn consent
        since they were enrolled.
        """
        self.ensure_one()
        if self.state != "active":
            return False, "Journey is %s." % self.state
        if self.journey_kind == "segment_scheduled" and self.segment_id and self.live_segment_sync:
            still_in = self.segment_id.membership_ids.filtered(
                lambda m, pid=member.partner_id.id: m.partner_id.id == pid and not m.exited_at
            )
            if not still_in:
                return False, (
                    "Party left audience segment '%s' while the journey was "
                    "running. Segment changes apply live on this journey." % self.segment_id.name
                )
        if self.exit_on_consent_withdrawal and member.partner_id:
            channel = CONSENT_CHANNEL_FOR.get(self.campaign_id.channel)
            if channel:
                verdict = self.env["fix.consent"].consent_check(
                    member.partner_id,
                    "marketing",
                    channel,
                    company=self.campaign_id.company_id,
                )
                if verdict["decision"] == "withdrawn":
                    return False, (
                        "Party withdrew marketing consent after enrolment. %s" % verdict["reason"]
                    )
        return True, ""

    def _runtime_execute_step(self, member, step):
        """Do what one step says. Returns the engine's outcome dict."""
        self.ensure_one()
        handler = getattr(self, "_step_%s" % step.step_type, None)
        if handler is None:
            return {
                "action": "fail",
                "reason": "Step type %r has no handler." % step.step_type,
            }
        return handler(member, step)

    # --- step handlers -------------------------------------------------
    def _step_wait(self, member, step):
        """A wait step's delay is applied when the member ENTERS it, by the
        engine. Arriving here means the wait has already elapsed."""
        return {"action": "next"}

    def _step_exit(self, member, step):
        return {
            "action": "exit",
            "reason": step.exit_reason or "Journey step '%s' ended the journey." % step.name,
        }

    def _step_send(self, member, step):
        """Queue a message on S1. The consent and BTRC decisions are S1's.

        A suppressed send does NOT stop the journey: the member moves on, and
        the delivery row records why nothing went out. Stopping would hide
        the suppression behind an exited member.
        """
        if not step.channel:
            return {"action": "fail", "reason": "Send step '%s' names no channel." % step.name}
        delivery = self.env["fix.notif.delivery"].queue(
            channel=step.channel,
            # Bound to the content, re-derived here and never read from the
            # stored step field (A03 audit G-M35-6).
            purpose=step._bound_purpose(),
            partner=member.partner_id,
            template=step.template_id or None,
            body=step.body or None,
            subject=step.subject or None,
            template_values={
                "name": member.partner_id.name or "",
                "campaign": self.campaign_id.name or "",
                "journey": self.name or "",
            },
            lawful_basis="consent",
            source_model="fix.campaign.journey.member",
            source_id=member.id,
            dedup_key="journey:%d:step:%d:member:%d" % (self.id, step.id, member.id),
            operating_unit=None,
            company=self.campaign_id.company_id,
        )
        member.sudo().write({"delivery_ids": [(4, delivery.id)], "last_send_state": delivery.state})
        return {"action": "next"}

    def _step_segment_add(self, member, step):
        if not step.segment_id:
            return {"action": "fail", "reason": "Segment step '%s' names no segment." % step.name}
        step.segment_id.sudo().action_add_members([member.partner_id.id])
        return {"action": "next"}

    def _step_segment_remove(self, member, step):
        if not step.segment_id:
            return {"action": "fail", "reason": "Segment step '%s' names no segment." % step.name}
        step.segment_id.sudo().action_remove_member(member.partner_id.id)
        return {"action": "next"}

    def _step_publish_event(self, member, step):
        """Hand off to another module through the outbox.

        This is how a journey awards loyalty points (M10) or raises a lead
        (M07) without cd_campaign depending on either: both are downstream of
        this module, so a direct call would be a dependency cycle. The
        consumer subscribes; the journey never reaches into it.
        """
        if not step.event_type:
            return {
                "action": "fail",
                "reason": "Publish step '%s' names no event type." % step.name,
            }
        payload = {
            "journey_id": self.id,
            "journey": self.name,
            "campaign_id": self.campaign_id.id,
            "partner_id": member.partner_id.id,
            "step": step.name,
            "note": step.event_note or "",
        }
        # Three literal calls rather than one with a variable event type: the
        # event-registry generator reads publish() CALL SITES statically, so a
        # computed event name is invisible to it and would never be checked
        # against the registry or given a schema.
        if step.event_type == "journey.loyalty_award_requested":
            publish(
                self.env,
                "journey.loyalty_award_requested",
                "fix.campaign.journey.member",
                member.id,
                payload,
            )
        elif step.event_type == "journey.lead_requested":
            publish(
                self.env,
                "journey.lead_requested",
                "fix.campaign.journey.member",
                member.id,
                payload,
            )
        elif step.event_type == "journey.followup_requested":
            publish(
                self.env,
                "journey.followup_requested",
                "fix.campaign.journey.member",
                member.id,
                payload,
            )
        else:
            return {
                "action": "fail",
                "reason": "Publish step '%s' names event type %r, which has no "
                "registered publisher branch." % (step.name, step.event_type),
            }
        return {"action": "next"}

    def _step_branch(self, member, step):
        """Evaluate the step's condition and go to one of two named steps."""
        result = step._evaluate(member)
        target = step.true_step_id if result else step.false_step_id
        if not target:
            # A branch arm with nowhere to go ends the journey for this member
            # rather than falling through to the next step in sequence, which
            # would silently merge the two arms.
            return {
                "action": "complete",
                "reason": "Branch '%s' took the %s arm, which has no next step."
                % (step.name, "true" if result else "false"),
            }
        return {"action": "goto", "next_step": target}

    # ------------------------------------------------------------------
    # Crons
    # ------------------------------------------------------------------
    @api.model
    def cron_advance_journeys(self, limit=500):
        """Walk every due member of every active journey."""
        # A journey under a campaign that is not running is skipped, not
        # walked: pausing the campaign pauses its journeys, and this is the
        # backstop for one paused by any other route (A03 audit G-M35-5).
        active = self.sudo().search(
            [("state", "=", "active"), ("campaign_id.state", "=", "running")]
        )
        if not active:
            return {"considered": 0}
        return active._runtime_advance_due(limit=limit)

    @api.model
    def cron_resync_live_segments(self):
        """Admit parties who joined a segment under a running journey.

        The live-republish behaviour D365 is shipping: a segment edited while
        a journey runs applies in real time. Departures are handled on the
        way out by the per-step eligibility check; this handles arrivals,
        which no per-member check can see.
        """
        journeys = self.sudo().search(
            [
                ("state", "=", "active"),
                ("journey_kind", "=", "segment_scheduled"),
                ("live_segment_sync", "=", True),
            ]
        )
        added = 0
        for journey in journeys:
            added += journey._enrol_segment_members()
        return {"journeys": len(journeys), "members_added": added}


class FixCampaignJourneyStep(models.Model):
    """One step of a journey. Ordered by sequence; branches name their arms."""

    _name = "fix.campaign.journey.step"
    _description = "Journey Step"
    _order = "journey_id, sequence, id"

    journey_id = fields.Many2one(
        "fix.campaign.journey", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(required=True, default=10)
    name = fields.Char(required=True)
    step_type = fields.Selection(STEP_TYPES, required=True, default="send")
    active = fields.Boolean(default=True)
    wait_minutes = fields.Integer(
        string="Wait Before This Step (min)",
        default=0,
        help="Applied when a member ENTERS this step. A 'Wait' step is just a "
        "step whose only job is this delay.",
    )
    # --- send ---
    channel = fields.Selection(STEP_CHANNELS, string="Channel")
    # A03 audit G-M35-6: the purpose was a free choice per step, so a
    # marketer put promotional copy on purpose='service_updates' and escaped
    # the BTRC curfew and the marketing-consent check. It is now derived from
    # the CONTENT: only a transactional template sent unedited is a service
    # update; anything with authored copy is marketing.
    purpose = fields.Selection(
        [
            ("marketing", "Marketing"),
            ("service_updates", "Service Updates"),
            ("research", "Research & Analytics"),
        ],
        compute="_compute_purpose",
        store=True,
        readonly=True,
        help="The processing purpose the consent decision is taken against. "
        "Set by the template's consent class, not chosen per step.",
    )
    template_id = fields.Many2one("fix.cc.notif.template", string="Message Template")
    subject = fields.Char(help="Overrides the template subject when set.")
    body = fields.Text(help="Overrides the template body when set.")
    # --- segment ---
    segment_id = fields.Many2one("fix.segment", string="Segment")
    # --- publish_event ---
    # A SELECTION, not free text. An arbitrary event type published into the
    # outbox has no schema, no registered consumer and no topic mapping: it is
    # a message nothing can receive. These three are the hand-offs the gap
    # plan names, and each is registered in contracts/events.
    event_type = fields.Selection(
        [
            ("journey.loyalty_award_requested", "Request a loyalty award (M10)"),
            ("journey.lead_requested", "Raise a sales lead (M07)"),
            ("journey.followup_requested", "Raise a CX follow-up (M34)"),
        ],
        string="Event Type",
        help="The outbox hand-off this step publishes. Restricted to events "
        "that have a registered schema and a consumer — a journey cannot "
        "invent an event nothing listens for.",
    )
    event_note = fields.Char(string="Event Note")
    # --- exit ---
    exit_reason = fields.Char()
    # --- branch ---
    condition_kind = fields.Selection(
        [
            ("always", "Always true"),
            ("partner_field", "Party field comparison"),
            ("responded", "Responded to this campaign"),
            ("consent_granted", "Marketing consent is granted"),
        ],
        default="always",
    )
    condition_field = fields.Selection(
        sorted(BRANCH_PARTNER_FIELDS.items()),
        string="Party Field",
        help="A whitelist. A journey is authored by a marketer, so it may not "
        "name arbitrary fields or evaluate expressions.",
    )
    condition_operator = fields.Selection(
        [
            ("=", "equals"),
            ("!=", "does not equal"),
            ("set", "is set"),
            ("unset", "is not set"),
            ("contains", "contains"),
        ],
        default="=",
    )
    condition_value = fields.Char()
    true_step_id = fields.Many2one(
        "fix.campaign.journey.step", string="If True, Go To", ondelete="set null"
    )
    false_step_id = fields.Many2one(
        "fix.campaign.journey.step", string="If False, Go To", ondelete="set null"
    )

    _sequence_unique = models.Constraint(
        "UNIQUE (journey_id, sequence)",
        "Two steps of one journey cannot share a sequence number — the order "
        "would be undefined.",
    )

    @api.constrains("step_type", "channel", "template_id", "body", "segment_id", "event_type")
    def _check_step_is_executable(self):
        """A step that cannot run must not save.

        The old steps_json blob could hold anything because nothing read it.
        These are real records now, so an unexecutable step is a defect that
        belongs at authoring time rather than at 03:00 in a cron log.
        """
        for rec in self:
            if rec.step_type == "send":
                if not rec.channel:
                    raise ValidationError("Send step '%s' needs a channel." % rec.name)
                if not (rec.template_id or (rec.body or "").strip()):
                    raise ValidationError(
                        "Send step '%s' needs a template or a body — there is "
                        "nothing to send otherwise." % rec.name
                    )
            if rec.step_type in ("segment_add", "segment_remove") and not rec.segment_id:
                raise ValidationError("Segment step '%s' needs a segment." % rec.name)
            if rec.step_type == "publish_event" and not (rec.event_type or "").strip():
                raise ValidationError("Publish step '%s' needs an event type." % rec.name)

    def _bound_purpose(self) -> str:
        """The purpose this step's content binds it to."""
        self.ensure_one()
        template = self.template_id
        authored = (self.body or "").strip() or (self.subject or "").strip()
        if template and template.consent_class == "transactional" and not authored:
            return "service_updates"
        return "marketing"

    @api.depends("step_type", "template_id", "template_id.consent_class", "body", "subject")
    def _compute_purpose(self):
        for rec in self:
            rec.purpose = rec._bound_purpose() if rec.step_type == "send" else False

    @api.constrains("purpose", "step_type", "template_id", "body", "subject")
    def _check_purpose_is_bound(self):
        for rec in self:
            if rec.step_type == "send" and rec.purpose != rec._bound_purpose():
                raise ValidationError(
                    "Send step '%s' cannot use purpose '%s': its content makes it a %s "
                    "message. The purpose follows the template's consent class, so "
                    "marketing copy is always sent as marketing."
                    % (rec.name, rec.purpose, rec._bound_purpose().replace("_", " "))
                )

    @api.constrains("true_step_id", "false_step_id", "journey_id")
    def _check_branch_arms_are_in_this_journey(self):
        for rec in self:
            for arm in (rec.true_step_id, rec.false_step_id):
                if arm and arm.journey_id != rec.journey_id:
                    raise ValidationError(
                        "Branch step '%s' points at a step of another journey." % rec.name
                    )

    def _evaluate(self, member):
        """The branch condition. Bounded by construction — no eval anywhere."""
        self.ensure_one()
        partner = member.partner_id
        kind = self.condition_kind or "always"
        if kind == "always":
            return True
        if kind == "responded":
            return bool(
                self.env["fix.campaign.response"]
                .sudo()
                .search_count(
                    [
                        ("campaign_id", "=", self.journey_id.campaign_id.id),
                        ("partner_id", "=", partner.id),
                    ]
                )
            )
        if kind == "consent_granted":
            channel = CONSENT_CHANNEL_FOR.get(self.journey_id.campaign_id.channel)
            if not channel:
                return False
            return self.env["fix.consent"].consent_check(partner, "marketing", channel)["allowed"]
        if kind == "partner_field":
            if not self.condition_field or self.condition_field not in BRANCH_PARTNER_FIELDS:
                return False
            value = partner[self.condition_field]
            # A Many2one compares on its display name, which is what a
            # marketer typed into the value box.
            if hasattr(value, "display_name"):
                value = value.display_name if value else ""
            operator = self.condition_operator or "="
            expected = self.condition_value or ""
            if operator == "set":
                return bool(value)
            if operator == "unset":
                return not bool(value)
            text = "" if value in (False, None) else str(value)
            if operator == "=":
                return text == expected
            if operator == "!=":
                return text != expected
            if operator == "contains":
                return expected.lower() in text.lower()
        return False


class FixCampaignJourneyMember(models.Model):
    """One party's progress through one journey."""

    _name = "fix.campaign.journey.member"
    _description = "Journey Member"
    _inherit = ["fix.step.member.mixin", "mail.thread"]
    _order = "next_action_at, id"
    _rec_name = "partner_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    journey_id = fields.Many2one(
        "fix.campaign.journey", required=True, ondelete="cascade", index=True
    )
    partner_id = fields.Many2one("res.partner", required=True, ondelete="cascade", index=True)
    current_step_id = fields.Many2one(
        "fix.campaign.journey.step", string="Current Step", ondelete="set null"
    )
    enrol_source = fields.Selection(
        [("launch", "Segment launch"), ("trigger", "Trigger event"), ("manual", "Manual")],
        required=True,
        default="launch",
    )
    source_event_id = fields.Char(
        index=True, help="The outbox event that admitted this member, if any."
    )
    enrol_key = fields.Char(
        required=True,
        index=True,
        help="Idempotency key: journey:party:event. A replayed event re-enrols "
        "nobody, which is what a trigger journey needs.",
    )
    delivery_ids = fields.Many2many("fix.notif.delivery", string="Messages Sent", readonly=True)
    last_send_state = fields.Char(readonly=True)

    _enrol_key_unique = models.Constraint(
        "UNIQUE (enrol_key)", "This party is already enrolled in this journey for that event."
    )
