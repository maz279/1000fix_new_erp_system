# cd_contact_centre — M27 Omnichannel Contact Centre + M32 Conversational AI
# (P07-M05, CD-M27-nn/CD-M32-nn). The notification half shipped in W1
# (ADR-022); this is the CONVERSATION half: unified channels, transcripts,
# the customer-360 view, and the M32 assistant's transactional intents with
# clean human handoff (G4-04/G4-05).
import base64
import hashlib

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .assistant_engine import ORDER_STATE_TEXT, normalize_text, scrub_pii

# Words that name the KIND of place, not WHICH branch: ignored when matching a
# branch the customer mentions ("Dhanmondi service centre" -> "dhanmondi").
_BRANCH_GENERIC_WORDS = {
    "1000fix",
    "branch",
    "centre",
    "center",
    "service",
    "services",
    "point",
    "outlet",
    "depot",
    "repair",
    "shop",
    "office",
    "শাখা",
    "সার্ভিস",
    "সেন্টার",
    "ব্রাঞ্চ",
    "পয়েন্ট",
    "১০০০ফিক্স",
}


def _answer(bn: str, en: str, grounded: bool, reason: str = "") -> dict:
    return {"bn": bn, "en": en, "grounded": grounded, "reason": reason}


CHANNELS = [
    ("voice", "Voice (Hotline 16743)"),
    ("whatsapp", "WhatsApp"),
    ("chat", "Web Chat"),
    ("email", "Email"),
    ("in_app", "In-App"),
    # M27 capture pass 2: inbound SMS replies (FR-CCE-012) and social
    # messaging (FR-CCE-013) are logged contacts too.
    ("sms", "SMS"),
    ("social", "Social Messaging"),
]


class FixConversation(models.Model):
    """One conversation on any channel, with its transcript. G4-04: hotline
    conversations captured in the system of record — the transcript IS the
    record. SC-003: transcripts exist for SERVICE; mining them for training
    needs a confirmed legal basis first (the flag enforces the pause)."""

    _name = "fix.conversation"
    _description = "Conversation"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "started_at desc, id desc"

    def _fix_guarded_fields(self) -> set:
        # REQ-27.1 (wrap-up) and REQ-27.2 (BTRC recording integrity) live in
        # action_resolve and attach_recording. A plain write closed calls with
        # no disposition or notes and planted an all-zero "digest" (A03 audit).
        return super()._fix_guarded_fields() | {
            "state",
            "ai_resolved",
            "recording_sha256",
            "recording_consent_state",
            "recording_consent_id",
            # Set by the dispatch hand-off; its presence stops a second dispatch.
            "field_work_order_ref",
            # Routing and service-level evidence (A03 audit M27 G7/G13): set
            # by intake, claim and assignment, never typed. Affinity routing
            # and the service-level alert read them.
            "agent_id",
            "queued_at",
            "answered_at",
            "work_item_id",
            "sla_answer_due_at",
        }

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    channel = fields.Selection(CHANNELS, required=True, default="voice", tracking=True)
    customer_id = fields.Many2one("res.partner", string="Customer", index=True, ondelete="set null")
    contact_identity = fields.Char(
        string="Contact Identity",
        help="The caller's number / WhatsApp JID / email — the join key when "
        "the party is not yet identified",
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("with_ai", "With AI Assistant"),
            ("with_agent", "With Agent"),
            ("resolved_ai", "Resolved by AI"),
            ("resolved_agent", "Resolved by Agent"),
            ("abandoned", "Abandoned"),
        ],
        default="new",
        required=True,
        tracking=True,
    )
    started_at = fields.Datetime(default=fields.Datetime.now, required=True)
    ended_at = fields.Datetime(readonly=True)
    turn_ids = fields.One2many("fix.conversation.turn", "conversation_id", string="Transcript")
    # M32 assistant fields
    ai_resolved = fields.Boolean(
        readonly=True, copy=False, help="G4-05: resolved by the assistant without an agent"
    )
    handoff_reason = fields.Char(readonly=True)
    intent = fields.Char(index=True, help="The classified transactional intent (bn/en)")
    call_sid = fields.Char(
        string="Call SID", index=True, help="Telephony session identifier from CPaaS (INT-015)"
    )
    pii_masked = fields.Boolean(
        string="PII Masked", default=False, help="SC-003: transcript masked for offline mining"
    )
    # M27 contact-centre operations: queue/agent/disposition/SLA capture.
    # Without these the queue, service-level and AHT reports have no basis.
    queue_id = fields.Many2one("fix.cc.queue", string="Queue", index=True)
    agent_id = fields.Many2one("res.users", string="Handling Agent", index=True)
    disposition_id = fields.Many2one("fix.cc.disposition", string="Disposition")
    queued_at = fields.Datetime(help="When the contact entered the queue.")
    answered_at = fields.Datetime(help="When an agent (or the AI) picked it up.")
    fcr = fields.Boolean(
        string="First-Contact Resolved",
        help="Set by the disposition category when the contact was resolved on this session.",
    )
    # BTRC compliance and Voice recording fields (FLAW-27.2)
    recording_url = fields.Char(string="Voice Recording URL")
    recording_sha256 = fields.Char(string="Recording SHA-256 Checksum", tracking=True)
    recording_retention_days = fields.Integer(
        string="BTRC Retention Days Left", compute="_compute_btrc_retention"
    )
    # --- Consent-gated recording (A03 gap-plan P0, W1) ----------------
    # The estate recorded, hashed and retained calls under BTRC's 180-day
    # rule but never checked whether it was ALLOWED to record. M33 has held a
    # PDPO-grade consent register the whole time; nothing joined them, so
    # every call was recorded without a consent decision. D365 shipped
    # consent-based recording GA 8 May 2026 -- for 1000FiX this was not a
    # missing feature but a live compliance exposure, with the parts to close
    # it already in the estate.
    recording_consent_state = fields.Selection(
        [
            ("not_checked", "Not checked"),
            ("granted", "Consent on file"),
            ("notice_announced", "Notice announced on the call"),
            ("legal_obligation", "Legal obligation (declared)"),
            ("refused", "Refused - not recorded"),
        ],
        string="Recording Consent",
        default="not_checked",
        readonly=True,
        copy=False,
        tracking=True,
        help="The basis on which this call was recorded, or the reason it was "
        "not. 'not_checked' means no recording was attempted.",
    )
    recording_consent_id = fields.Many2one(
        "fix.consent",
        string="Decisive Recording Consent",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
    recording_notice_id = fields.Many2one(
        "fix.transparency.notice",
        string="Recording Notice Announced",
        readonly=True,
        copy=False,
        help="The transparency-notice version read to the caller before "
        "recording began. For an unidentified caller that announcement is the "
        "only lawful basis available, so it is evidence, not decoration.",
    )
    recording_notice_at = fields.Datetime(string="Notice Announced At", readonly=True, copy=False)
    recording_refusal_reason = fields.Text(
        string="Recording Refusal Reason",
        readonly=True,
        copy=False,
        help="Why a recording was refused. Kept so that the ABSENCE of a "
        "recording is itself explained in the record.",
    )
    wrapup_notes = fields.Text(string="Wrap-Up Notes", tracking=True)
    csat_dispatched_at = fields.Datetime(
        string="CSAT Survey Dispatched At",
        readonly=True,
        copy=False,
        help="REQ-27.5: stamped when the post-call satisfaction survey goes "
        "out. Set only when a message was actually queued on the delivery "
        "service, never merely when dispatch was attempted.",
    )
    csat_suppressed_reason = fields.Char(
        string="CSAT Not Sent Because",
        readonly=True,
        copy=False,
        help="Why no satisfaction survey went out: an anonymous caller, or a "
        "consent refusal. Kept so the absence of a CSAT response is "
        "explained rather than counted as a non-response.",
    )
    urgency_level = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical / Emergency"),
        ],
        default="medium",
        string="Urgency Level",
    )
    field_work_order_ref = fields.Char(
        string="Dispatched Field Order Ref (M02)",
        readonly=True,
        help="Reference to created field work order (fix.field.order or fix.work.order)",
    )
    # --- Routing (A03 audit M27 G7) ------------------------------------
    # Conversations never became work items: routing, presence and capacity
    # ran beside the contact and were never joined to it. Intake now creates
    # the work item, and the conversation owns its lifecycle.
    work_item_id = fields.Many2one(
        "fix.routing.workitem",
        string="Routed Work Item",
        readonly=True,
        copy=False,
        index=True,
        ondelete="set null",
    )
    routing_note = fields.Char(
        readonly=True,
        copy=False,
        help="Why this contact is not routed, when it is not. A contact with no "
        "work item and no reason would be invisible to every queue.",
    )
    sla_answer_due_at = fields.Datetime(
        string="Answer Due By (SLA)",
        readonly=True,
        copy=False,
        help="The deadline of this contact's answer-time SLA instance (S9).",
    )

    @api.depends("channel", "customer_id.name", "contact_identity")
    def _compute_display_name(self):
        # No name field: QA, script-adherence and work-item rows rendered
        # "fix.conversation,12". Channel + who is what a supervisor scans for.
        channels = dict(self._fields["channel"].selection)
        for conv in self:
            who = conv.customer_id.name or conv.contact_identity or "অজ্ঞাত (unidentified)"
            conv.display_name = "%s #%s · %s" % (
                channels.get(conv.channel, conv.channel),
                conv.id,
                who,
            )

    @api.depends("started_at")
    def _compute_btrc_retention(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.started_at:
                age_days = (now - rec.started_at).days
                rec.recording_retention_days = max(0, 180 - age_days)
            else:
                rec.recording_retention_days = 180

    _CLOSED_STATES = ("resolved_ai", "resolved_agent", "abandoned")

    # ------------------------------------------------------------------
    # Routing: the conversation owns its work item (A03 audit M27 G7)
    # ------------------------------------------------------------------
    # One owner, so the two cannot drift: conversation transitions drive the
    # work item (claim, resolve, return to AI, abandon). The only flow in the
    # other direction is an ASSIGNMENT made by the router or a supervisor,
    # which stamps the agent on the conversation (_mark_answered). A work item
    # of an open conversation cannot be closed on its own; see
    # fix.routing.workitem.close_and_release.
    def _route_contact(self):
        """Make sure each open contact has a live work item in a queue."""
        Workstream = self.env["fix.routing.workstream"].sudo()
        for conv in self:
            if conv.state in self._CLOSED_STATES:
                continue
            item = conv.work_item_id
            if item and item.state not in ("closed", "abandoned"):
                continue
            workstream = Workstream.for_conversation(conv)
            if not workstream:
                conv._guarded().write(
                    {
                        "routing_note": "No active routing workstream serves the %s "
                        "channel, so this contact is in no queue. Configure one "
                        "(M27 Unified Routing)." % conv.channel
                    }
                )
                continue
            item = workstream.intake(
                "fix.conversation",
                conv.id,
                partner=conv.customer_id,
                context_values={"urgency_level": conv.urgency_level, "intent": conv.intent or ""},
            )
            conv._guarded().write(
                {
                    "work_item_id": item.id,
                    "queue_id": item.queue_id.id,
                    "queued_at": conv.queued_at or fields.Datetime.now(),
                    "routing_note": False,
                }
            )
            conv._open_answer_sla()

    def _mark_answered(self, agent):
        """An agent now handles the contact: stamp who and when (G13)."""
        for conv in self:
            vals = {"agent_id": agent.id}
            if not conv.answered_at:
                vals["answered_at"] = fields.Datetime.now()
            if conv.state in ("new", "with_ai"):
                vals["state"] = "with_agent"
            conv._guarded().write(vals)
            conv._close_answer_sla("answered")

    def _close_work_item(self, reason: str, abandoned: bool = False):
        """Close (or abandon) the contact's live work item from the owner side."""
        for conv in self:
            item = conv.work_item_id
            if not item or item.state in ("closed", "abandoned"):
                continue
            if abandoned:
                item._guarded().action_abandon(reason)
            else:
                item._guarded().close_and_release(session_closed=True, reason=reason)

    # ------------------------------------------------------------------
    # Per-contact answer SLA (S9; A03 audit M27 G6/G13)
    # ------------------------------------------------------------------
    # fix.sla.kpi.instance lives in cd_service_order, which this module does
    # not depend on (it would pull the whole service-order stack into the
    # contact centre). The engine is reached through the registry instead, the
    # same soft coupling the field dispatch and the entitlement lookup use.
    # The target is the queue's own answer target, so no new number is set.
    _ANSWER_KPI = "first_response"

    def _sla_engine(self):
        return self.env.get("fix.sla.kpi.instance")

    def _contact_sla_policy(self):
        """The answer-time policy for this contact's queue (created on first use)."""
        self.ensure_one()
        Policy = self.env["fix.sla.policy"].sudo()
        queue = self.queue_id
        seconds = queue.target_answer_seconds or 20
        hours = round(seconds / 3600.0, 6)
        code = ("CC-%s" % (queue.code or "DEFAULT"))[:16]
        policy = Policy.with_context(active_test=False).search([("code", "=", code)], limit=1)
        vals = {"response_hours": hours, "resolution_hours": hours}
        if not policy:
            # service_type is a service-delivery dimension with no contact-centre
            # value; the CC- code is what identifies this policy.
            return Policy.create(
                dict(
                    vals,
                    code=code,
                    name="Hotline 16743 answer target: %s" % (queue.name or "default queue"),
                    service_type="walk_in",
                    priority="normal",
                    company_id=self.company_id.id,
                )
            )
        if abs(policy.response_hours - hours) > 1e-6:
            policy.write(vals)
        return policy

    def _open_answer_sla(self):
        Instance = self._sla_engine()
        if Instance is None or "fix.sla.policy" not in self.env:
            return
        for conv in self:
            if not conv.queue_id or conv.answered_at:
                continue
            instance = Instance.sudo().start_for(
                conv,
                conv._contact_sla_policy(),
                self._ANSWER_KPI,
                partner=conv.customer_id,
                started_at=conv.queued_at or fields.Datetime.now(),
            )
            conv._guarded().write({"sla_answer_due_at": instance.target_at})

    def _close_answer_sla(self, outcome: str):
        """Finish the live answer clock: met, missed, or not applicable."""
        Instance = self._sla_engine()
        if Instance is None:
            return
        now = fields.Datetime.now()
        for conv in self:
            for inst in Instance.sudo().for_record(conv, self._ANSWER_KPI):
                late = inst.target_at and now > inst.target_at
                if late and outcome in ("answered", "abandoned"):
                    # Answered or abandoned after the target is a breach,
                    # whether or not the breach cron has run yet.
                    inst.write({"state": "breached", "breached_at": now})
                elif outcome == "answered":
                    inst.succeed(when=now)
                elif outcome == "abandoned":
                    inst.cancel("Caller abandoned before the answer target.")
                else:
                    inst.cancel("Resolved by the assistant; no agent answer was needed.")

    def action_claim(self):
        """An agent takes a new or AI conversation (call control 'claim')."""
        for conversation in self:
            # A handed-off contact waits as with_agent with no agent yet.
            waiting = conversation.state == "with_agent" and not conversation.agent_id
            if conversation.state not in ("new", "with_ai") and not waiting:
                raise UserError("Only a new or AI-handled conversation can be claimed")
            item = conversation.work_item_id
            if (
                item
                and item.state in ("assigned", "active")
                and item.assigned_agent_id
                and item.assigned_agent_id != self.env.user
            ):
                raise UserError(
                    "This contact is assigned to %s. A supervisor reassigns it; it "
                    "cannot be claimed past the routing decision." % item.assigned_agent_id.name
                )
            conversation._mark_answered(self.env.user)
            if item and item.state in ("pending", "offered"):
                item._guarded()._assign_to(self.env.user, mode="pick", enforce_capacity=False)
            if item and item.state == "assigned":
                item._guarded().action_start_work()

    def action_return_to_ai(self, reason: str = ""):
        """Hand an open conversation back to the AI lane, with its reason."""
        for conversation in self:
            if conversation.state in self._CLOSED_STATES:
                raise UserError("A closed conversation cannot be handed back to the AI")
            conversation._guarded().write({"state": "with_ai", "handoff_reason": reason})
            # The agent is no longer working it: give the capacity back. A
            # later hand-off routes a fresh work item.
            conversation._close_work_item("returned to the AI assistant: %s" % (reason or "-"))

    def _mark_call_ended(self):
        """Hang-up before wrap-up: the call is over, the after-call work is not.

        A caller who hangs up before any agent answered was never served: that
        is an abandoned contact (G13), not after-call work."""
        for conv in self:
            if not conv.answered_at and not conv.agent_id:
                conv._mark_abandoned()
            else:
                conv._guarded().write({"ended_at": fields.Datetime.now(), "state": "with_agent"})

    def _mark_abandoned(self):
        for conv in self:
            if conv.state in self._CLOSED_STATES:
                continue
            conv._guarded().write({"state": "abandoned", "ended_at": fields.Datetime.now()})
            conv._close_work_item("caller abandoned before an agent answered", abandoned=True)
            conv._close_answer_sla("abandoned")

    def action_handoff_to_agent(self, reason: str = ""):
        """T07: the human-handoff path with FULL context transfer — the
        agent sees the entire transcript, the intent and the customer 360."""
        for conversation in self:
            if conversation.state in self._CLOSED_STATES:
                # It had no state check: a hand-off reopened a resolved call (C3).
                raise UserError("A closed conversation cannot be handed off.")
            conversation._guarded().write({"state": "with_agent", "handoff_reason": reason})
            conversation._route_contact()
            publish(
                self.env,
                "conversation.handed_off",
                "fix.conversation",
                conversation.id,
                {
                    "channel": conversation.channel,
                    "intent": conversation.intent,
                    "reason": reason,
                    "turns": len(conversation.turn_ids),
                },
            )

    def action_resolve(self, by_ai: bool = False):
        for conversation in self:
            if not by_ai:
                if not conversation.disposition_id:
                    raise ValidationError(
                        "Mandatory wrap-up required: Please select a primary disposition code before resolving the ticket (FLAW-27.1 / REQ-27.1)."
                    )
                notes = (conversation.wrapup_notes or "").strip()
                if not notes:
                    raise ValidationError(
                        "Mandatory wrap-up required: Please enter wrap-up notes before resolving the ticket (REQ-27.1)."
                    )
                # REQ-27.1 asks for *substantive* notes. The gate used to accept
                # any non-empty string, so calls closed on "ok" (audit 2026-10-31).
                if len(notes) < 20:
                    raise ValidationError(
                        "Wrap-up too short: REQ-27.1 requires at least 20 characters "
                        "of substantive summary; %d given." % len(notes)
                    )

            # REQ-27.2 / BTRC: a voice call closes only with a verified digest
            # OF THE AUDIO. This used to compute sha256(recording_url) — a
            # digest of the URL string, which the file behind it can change
            # freely without breaking (audit 2026-10-31). A digest is now
            # produced by attach_recording() from the bytes, and resolving
            # without one is refused rather than papered over.
            if (
                conversation.channel == "voice"
                and conversation.recording_url
                and (not conversation.recording_sha256 or len(conversation.recording_sha256) != 64)
            ):
                raise ValidationError(
                    "BTRC recording integrity: this call carries a recording "
                    "URL but no SHA-256 digest of the audio. Attach the "
                    "recording through attach_recording() so the digest is "
                    "taken from the file itself (REQ-27.2)."
                )

            if conversation.state in self._CLOSED_STATES:
                raise UserError("This conversation is already closed (%s)." % conversation.state)
            conversation._guarded().write(
                {
                    "state": "resolved_ai" if by_ai else "resolved_agent",
                    "ai_resolved": by_ai,
                    "ended_at": fields.Datetime.now(),
                }
            )
            # The conversation owns its work item: resolving ends the session
            # and releases the agent's capacity (A03 audit M27 G7).
            conversation._close_work_item("conversation resolved")
            conversation._close_answer_sla("answered" if conversation.answered_at else "ai")
            publish(
                self.env,
                "conversation.resolved",
                "fix.conversation",
                conversation.id,
                {
                    "by_ai": by_ai,
                    "intent": conversation.intent,
                    "disposition": conversation.disposition_id.name
                    if conversation.disposition_id
                    else None,
                    "fcr": conversation.fcr,
                },
            )
            conversation._dispatch_csat_survey()

    def action_wrap_up(self, disposition_id=None, wrapup_notes="", fcr=False):
        """FR-CCE-033 / BRU-CCE-11: the agent's wrap-up, in one step.

        The workspace Agent Desktop page used to offer "+ New Disposition
        Code" (configuration) and no way for an agent to record the outcome of
        the contact they had just handled: the disposition and notes had to be
        typed on the record and Resolve found on another list. This takes
        both and closes the conversation through action_resolve, so every
        gate there (disposition, substantive notes, recording digest) still
        decides. Only the handling agent or a contact-centre supervisor may
        close an agent's conversation.
        """
        self.ensure_one()
        if self.state != "with_agent":
            raise UserError(
                "Only a conversation an agent is handling is wrapped up; this one is %s."
                % dict(self._fields["state"].selection).get(self.state, self.state)
            )
        if (
            self.agent_id
            and self.agent_id != self.env.user
            and not self.env.su
            and not self.env.user.has_group("cd_contact_centre.group_cc_supervisor")
        ):
            raise AccessError(
                "This conversation is handled by %s: only that agent or a contact-centre "
                "supervisor wraps it up." % self.agent_id.name
            )
        disposition = (
            self.env["fix.cc.disposition"].browse(int(disposition_id)).exists()
            if disposition_id
            else self.env["fix.cc.disposition"]
        )
        if not disposition:
            raise ValidationError(
                "Choose the disposition: a conversation cannot close without one (BRU-CCE-11)."
            )
        self.write(
            {
                "disposition_id": disposition.id,
                "wrapup_notes": (wrapup_notes or "").strip() or False,
                "fcr": bool(fcr),
            }
        )
        self.action_resolve()
        return True

    # --- Consent-gated recording --------------------------------------
    def action_announce_recording_notice(self, notice=None):
        """Record that the recording notice was READ TO THE CALLER.

        For an identified party a stored consent record is the basis. On the
        16743 hotline most callers are not identified when the call connects,
        and the lawful mechanism there is the announcement at the head of the
        call -- so this stamps that it happened, against a real transparency
        notice version. The telephony layer calls it after the prompt plays.
        It is never inferred: a basis nobody can evidence is not a basis.
        """
        self.ensure_one()
        notice_rec = (
            notice
            if hasattr(notice, "id")
            else (self.env["fix.transparency.notice"].browse(notice) if notice else None)
        )
        if not notice_rec or not notice_rec.exists():
            raise ValidationError(
                "Announcing a recording notice requires the transparency-notice "
                "version that was read out. An announcement without a version "
                "cannot be evidenced (BRU-CPM-08)."
            )
        self.write(
            {
                "recording_notice_id": notice_rec.id,
                "recording_notice_at": fields.Datetime.now(),
            }
        )
        return True

    def recording_permitted(self, basis="consent", statutory_reference=""):
        """May this call be recorded? Ask BEFORE recording, not after.

        The telephony layer should call this at call setup, because the only
        way to honour a refusal is to never capture the audio.
        attach_recording() applies the same decision as a backstop for
        anything that captured first.

        Returns {allowed, state, reason, consent_id}.
        """
        self.ensure_one()
        if basis == "legal_obligation":
            if not (statutory_reference or "").strip():
                return {
                    "allowed": False,
                    "state": "refused",
                    "reason": "A legal-obligation basis for recording must cite the "
                    "instrument that imposes it. An uncited obligation is an "
                    "assertion, not a basis.",
                    "consent_id": False,
                }
            return {
                "allowed": True,
                "state": "legal_obligation",
                "reason": "Recorded under a declared legal obligation: %s."
                % statutory_reference.strip(),
                "consent_id": False,
            }
        if self.customer_id:
            verdict = self.env["fix.consent"].consent_check(
                self.customer_id, "call_recording", "voice", company=self.company_id
            )
            if verdict["allowed"]:
                return {
                    "allowed": True,
                    "state": "granted",
                    "reason": verdict["reason"],
                    "consent_id": verdict["consent_id"],
                }
            # A withdrawal by an identified party is decisive, and the
            # head-of-call announcement does not override it.
            if verdict["decision"] == "withdrawn":
                return {
                    "allowed": False,
                    "state": "refused",
                    "reason": verdict["reason"],
                    "consent_id": verdict["consent_id"],
                }
        if self.recording_notice_id and self.recording_notice_at:
            return {
                "allowed": True,
                "state": "notice_announced",
                "reason": "Recording notice version %s was read to the caller at "
                "%s and the call continued."
                % (self.recording_notice_id.version, self.recording_notice_at),
                "consent_id": False,
            }
        return {
            "allowed": False,
            "state": "refused",
            "reason": "No consent record for call recording and no recording "
            "notice was announced on this call. Absence of a basis is a refusal, "
            "not a permission (PDPO; D365-parity consent-based recording).",
            "consent_id": False,
        }

    def attach_recording(
        self,
        attachment_id=None,
        audio_bytes=None,
        url=None,
        basis="consent",
        statutory_reference="",
    ):
        """REQ-27.2: register a call recording and digest THE AUDIO.

        BTRC requires tamper-proof retention for 180 days. A digest is only
        evidence if it is taken over the bytes: the previous implementation
        hashed the recording URL, which the file behind it can change without
        breaking (audit 2026-10-31). Pass either a stored ir.attachment or the
        raw bytes; a bare URL is refused because it cannot be digested.

        Consent gate (A03 gap-plan P0): the recording is STORED only when
        recording_permitted() allows it. On a refusal this method deliberately
        does NOT raise -- it stamps the refusal, publishes a compliance event
        and returns None, so the refusal is persisted and auditable instead of
        being rolled back along with the exception. A caller that gets None
        must discard the audio it is holding.
        """
        self.ensure_one()
        # The PAYLOAD is validated first, and the consent gate second. A bare
        # URL cannot be digested and is a malformed call however the consent
        # question comes out, so REQ-27.2's refusal must not depend on it;
        # consent decides whether to STORE, not whether the call was wellformed.
        payload = audio_bytes
        if payload is None and attachment_id:
            attachment = self.env["ir.attachment"].browse(attachment_id).exists()
            if not attachment:
                raise ValidationError("Recording attachment %s not found." % attachment_id)
            payload = base64.b64decode(attachment.datas or b"")
            url = url or ("/web/content/%d" % attachment.id)
        if not payload:
            raise ValidationError(
                "A call recording must be supplied as bytes or a stored "
                "attachment so its SHA-256 digest can be taken from the audio "
                "itself. A URL alone is not tamper evidence (REQ-27.2)."
            )
        verdict = self.recording_permitted(basis=basis, statutory_reference=statutory_reference)
        if not verdict["allowed"]:
            self._guarded().write(
                {
                    "recording_consent_state": "refused",
                    "recording_refusal_reason": verdict["reason"],
                    "recording_consent_id": verdict["consent_id"] or False,
                }
            )
            publish(
                self.env,
                "conversation.recording_refused",
                "fix.conversation",
                self.id,
                {
                    "channel": self.channel,
                    "partner_id": self.customer_id.id or None,
                    "reason": verdict["reason"],
                    "basis_attempted": basis,
                },
            )
            return None
        digest = hashlib.sha256(payload).hexdigest()
        self._guarded().write(
            {
                "recording_url": url or self.recording_url,
                "recording_sha256": digest,
                "recording_consent_state": verdict["state"],
                "recording_consent_id": verdict["consent_id"] or False,
                "recording_refusal_reason": False,
            }
        )
        publish(
            self.env,
            "conversation.recording_attached",
            "fix.conversation",
            self.id,
            {
                "sha256": digest,
                "bytes": len(payload),
                "retention_days": self.recording_retention_days,
                "consent_basis": verdict["state"],
                "consent_id": verdict["consent_id"] or None,
            },
        )
        return digest

    def verify_recording_integrity(self, audio_bytes):
        """Re-digest supplied audio and report whether it still matches."""
        self.ensure_one()
        if not self.recording_sha256:
            return False
        return hashlib.sha256(audio_bytes).hexdigest() == self.recording_sha256

    # Conversation channels are not delivery channels: a voice call is
    # followed up by SMS, and a web-chat session by an in-app push. Kept as
    # one map so the choice is visible rather than re-derived per caller.
    _CSAT_DELIVERY_CHANNEL = {
        "voice": "sms",
        "whatsapp": "whatsapp",
        "email": "email",
        "chat": "push",
        "in_app": "push",
    }

    def _csat_target(self):
        """Where to send the CSAT invitation, or why we cannot.

        Returns (channel, address, reason). An anonymous caller who withheld
        their number is a real and common case on a hotline, so "nobody to
        write to" is an ANSWER here rather than an exception: S1 rightly
        refuses to invent a destination, and a conversation must remain
        resolvable either way. Refusing to let an agent close a call because
        the caller cannot be surveyed would be a far worse failure than an
        unsent survey.
        """
        self.ensure_one()
        channel = self._CSAT_DELIVERY_CHANNEL.get(self.channel, "sms")
        address = (self.contact_identity or "").strip()
        if not address and self.customer_id:
            partner = self.customer_id
            if channel == "email":
                address = (partner.email or "").strip()
            else:
                address = (getattr(partner, "mobile", False) or partner.phone or "").strip()
        if not address:
            return (
                None,
                None,
                (
                    "No contact identity on the conversation and none on file for "
                    "the party, so the satisfaction survey cannot be addressed."
                ),
            )
        return channel, address, ""

    def _dispatch_csat_survey(self):
        """REQ-27.5: a transactional CSAT survey within 5 minutes of the call.

        This used to publish an event and stamp a timestamp, which recorded
        our INTENTION to ask rather than a message. It now queues a real row
        on the S1 delivery service, so the estate can answer whether the
        customer was actually asked, on what channel, under what basis and at
        what cost.

        csat_dispatched_at is stamped ONLY when a message was queued. Stamping
        it either way would repeat the exact fault being corrected in M34,
        where a state meaning "we tried" was read as "we asked" and the CSAT
        basis counted surveys nobody received.

        Lawful basis is 'contract', declared and recorded: the customer is
        being asked about a repair they themselves commissioned, which is
        performance of that engagement rather than marketing. The basis is on
        every delivery row, so if Legal rules otherwise the affected sends can
        be found and the one declaration changed.
        """
        Delivery = self.env["fix.notif.delivery"]
        for conversation in self:
            if conversation.csat_dispatched_at:
                continue
            channel, address, reason = conversation._csat_target()
            if not channel:
                conversation.csat_suppressed_reason = reason
                publish(
                    self.env,
                    "conversation.csat_survey_withheld",
                    "fix.conversation",
                    conversation.id,
                    {
                        "partner_id": conversation.customer_id.id or None,
                        "channel": None,
                        "reason": reason,
                    },
                )
                continue
            body = (
                "1000FiX Services: আপনার সেবা কেমন ছিল? ১-৫ স্কেলে উত্তর দিন। / "
                "How was your service? Reply 1-5. Hotline 16743"
            )
            delivery = Delivery.queue(
                channel=channel,
                purpose="service_updates",
                partner=conversation.customer_id or None,
                to_address=address,
                body=body,
                lawful_basis="contract",
                source_model="fix.conversation",
                source_id=conversation.id,
                dedup_key="csat:conversation:%d" % conversation.id,
                operating_unit=conversation.operating_unit_id,
                company=conversation.company_id,
            )
            if delivery.state == "suppressed":
                conversation.csat_suppressed_reason = delivery.consent_reason
                publish(
                    self.env,
                    "conversation.csat_survey_withheld",
                    "fix.conversation",
                    conversation.id,
                    {
                        "partner_id": conversation.customer_id.id or None,
                        "channel": channel,
                        "reason": delivery.consent_reason,
                        "delivery_id": delivery.id,
                    },
                )
                continue
            conversation.write(
                {
                    "csat_dispatched_at": fields.Datetime.now(),
                    "csat_suppressed_reason": False,
                }
            )
            publish(
                self.env,
                "conversation.csat_survey_dispatched",
                "fix.conversation",
                conversation.id,
                {
                    "partner_id": conversation.customer_id.id,
                    "contact_identity": conversation.contact_identity,
                    "channel": channel,
                    "scale": "1-5",
                    "delivery_id": delivery.id,
                    "delivery_state": delivery.state,
                },
            )

    def action_create_field_work_order(self):
        """HS-03: Hotline 16743 urgent on-site repair dispatch to M02.

        This used to create fix.field.order from a customer_id it does not
        have, missing the service order and zone it requires, so the button
        could only fail (A03 audit, M27 G6). A field order is the dispatch of
        a SERVICE ORDER, so the hand-off now opens an on-site service order
        for the customer's registered device and hands it to M02 through the
        service order's own bridge, which resolves the zone, operating unit
        and SLA deadline. The service order carries an idempotency key per
        conversation, so a repeated click cannot open a second job.
        """
        if "fix.field.order" not in self.env or "fix.service.order" not in self.env:
            raise UserError(
                "Field dispatch is not available: the service order and field "
                "service modules are not installed."
            )
        for rec in self:
            if not rec.customer_id:
                raise ValidationError(
                    "Cannot create field work order: Customer must be identified."
                )
            if rec.field_work_order_ref:
                raise UserError(
                    "This conversation was already dispatched as field order %s."
                    % rec.field_work_order_ref
                )
            device = self.env["fix.device"].search(
                [("owner_id", "child_of", rec.customer_id.commercial_partner_id.id)],
                order="id desc",
                limit=1,
            )
            if not device:
                raise UserError(
                    "Cannot dispatch: %s has no registered device. Register the "
                    "device (M17) so the on-site job knows what it is repairing."
                    % rec.customer_id.display_name
                )
            branch = device.branch_id
            if not branch and rec.operating_unit_id:
                branch = self.env["fix.branch"].search(
                    [("operating_unit_id", "=", rec.operating_unit_id.id)], limit=1
                )
            if not branch:
                raise UserError(
                    "Cannot dispatch: no branch is known for this customer's device "
                    "or this conversation's operating unit."
                )
            critical = rec.urgency_level == "critical"
            order = self.env["fix.service.order"].create(
                {
                    "idempotency_key": "hotline-dispatch-conversation-%d" % rec.id,
                    "customer_id": rec.customer_id.id,
                    "device_id": device.id,
                    "branch_id": branch.id,
                    "operating_unit_id": (rec.operating_unit_id or branch.operating_unit_id).id,
                    "service_type": "onsite",
                    "priority": "emergency" if critical else "urgent",
                    "fault_description": rec.wrapup_notes
                    or ("Hotline 16743 Call Dispatch: " + (rec.intent or "Emergency Repair")),
                }
            )
            fwo = order.field_order_ids.filtered(lambda f: f.state != "cancelled")[:1]
            if not fwo:
                fwo = order.action_create_field_order()
            fwo.write(
                {
                    "priority": "3" if critical else "2",
                    "notes": "Hotline 16743 conversation %s. Contact: %s"
                    % (rec.display_name, rec.contact_identity or rec.customer_id.phone or "-"),
                }
            )
            rec._guarded().write({"field_work_order_ref": fwo.name})
            publish(
                self.env,
                "hotline.emergency_dispatch",
                "fix.conversation",
                rec.id,
                {
                    "customer_id": rec.customer_id.id,
                    "phone": rec.contact_identity,
                    "intent": rec.intent,
                    "service_order": order.name,
                    "work_order_ref": fwo.name,
                },
            )

    @api.model
    def resolution_rate(self) -> float:
        """G4-05 measured the honest way: AI resolutions against FIRST
        CONTACTS with handoffs (not against total sessions)."""
        ai = self.search_count([("ai_resolved", "=", True)])
        handoffs = self.search_count([("handoff_reason", "!=", False)])
        total = ai + handoffs
        return round(100.0 * ai / total, 2) if total else 0.0

    @api.model
    def intake_hotline_call(
        self, caller_phone: str, call_sid: str = "", initial_utterance: str = "", lang: str = "bn"
    ):
        """INT-015: Inbound call on Hotline 16743 creates conversation in record (G4-04)."""
        partner = self.env["res.partner"].search([("phone", "=", caller_phone)], limit=1)
        ou = self.env["operating.unit"].search([], limit=1)
        conv = self._guarded().create(
            {
                "channel": "voice",
                "contact_identity": caller_phone,
                "call_sid": call_sid,
                "customer_id": partner.id if partner else False,
                "operating_unit_id": ou.id if ou else False,
                "state": "with_ai",
                "started_at": fields.Datetime.now(),
            }
        )
        # Drop the transition token: the record goes back to the caller, and a
        # record carrying it would let every later write skip the guard.
        conv = self.browse(conv.id)
        greeting_bn = "১০০০ফিক্স কাস্টমার কেয়ারে আপনাকে স্বাগতম। আপনি কিভাবে সাহায্য চান?"
        greeting_en = "Welcome to 1000FiX Customer Care. How can we assist you today?"
        self.env["fix.conversation.turn"].create(
            {
                "conversation_id": conv.id,
                "sequence": 10,
                "speaker": "ai",
                "text": greeting_bn if lang == "bn" else greeting_en,
                "lang": lang,
            }
        )
        publish(
            self.env,
            "conversation.hotline_captured",
            "fix.conversation",
            conv.id,
            {
                "channel": "voice",
                "caller": caller_phone,
                "call_sid": call_sid,
            },
        )
        # A03 audit M27 G7: every contact becomes a routed work item.
        conv._route_contact()
        if initial_utterance:
            conv.intake_message(initial_utterance, speaker="customer", lang=lang)
        return conv

    # What the bot says when it may not answer: a guardrail blocked the turn,
    # or the drafted answer must be reviewed by a person first. Never the
    # blocked or unreviewed text itself.
    _HOLD_REPLY = {
        "bn": "আপনার প্রশ্নের নির্ভুল উত্তরের জন্য একজন কাস্টমার কেয়ার প্রতিনিধির সাথে যুক্ত করছি।",
        "en": "Connecting you with a customer care specialist to assist you accurately.",
    }

    def intake_message(self, text: str, speaker: str = "customer", lang: str = "bn"):
        """Records a transcript turn and triggers transactional AI dialogue management.

        A03 audit M32 G3: the live bot used to classify and answer on its own,
        so a text that a blocking guardrail refused in ask() was answered and
        closed as resolved_ai, with no audit row. Every bot answer now goes
        through the S7 ask() pipeline (guardrails, grounding, audit row), and
        only an answer ask() lets through, and that needs no human review, is
        sent and counted as an AI resolution.
        """
        Ask = self.env["fix.assistant.intent"]
        for conv in self:
            # A03 audit M27 G7: every contact is routed, whatever its channel.
            conv._route_contact()
            seq = (max(conv.turn_ids.mapped("sequence"), default=0) + 10) if conv.turn_ids else 10
            self.env["fix.conversation.turn"].create(
                {
                    "conversation_id": conv.id,
                    "sequence": seq,
                    "speaker": speaker,
                    "text": text,
                    "lang": lang,
                }
            )
            if speaker == "customer" and conv.state in ("new", "with_ai"):
                engine, _release = self.env["fix.assistant.dataset"].runtime_engine()
                # T-05: per-intent calibrated thresholds (M32 capture pass 2).
                res = engine.classify_intent(
                    text, self.env["fix.assistant.intent"].confidence_thresholds()
                )
                conv.write({"intent": res.matched_intent or ""})
                confident = bool(res.resolvable or getattr(res, "requires_grounding", False))
                # An unconfident guess is written on the conversation for the
                # record, but must not be answered: ask() would otherwise
                # ground on conversation.intent and send the authored answer
                # for a message the gate said to clarify (REQ-32.1; found by
                # M32 capture pass 2 - per-intent thresholds had no effect).
                asker = Ask if confident else Ask.with_context(assistant_intent_unconfirmed=True)
                result = asker.ask(
                    text,
                    intent=res.matched_intent if confident else None,
                    conversation=conv,
                    consumer="m27_bot",
                    language=lang if lang in ("bn", "en") else "bn",
                )
                ask_row = self.env["fix.assistant.ask"].sudo().browse(result.get("ask_id"))
                sendable = result.get("ok") and not result.get("requires_human")
                if sendable:
                    reply = result.get("bn") if lang == "bn" else result.get("en")
                    reply = reply or result.get("bn") or result.get("en")
                    handoff_reason = ""
                elif ask_row.guardrail_verdict == "blocked":
                    reply = self._HOLD_REPLY["bn" if lang == "bn" else "en"]
                    handoff_reason = "guardrail_blocked"
                elif result.get("ok"):
                    # Drafted (e.g. generated) but needs a person first (G12).
                    reply = self._HOLD_REPLY["bn" if lang == "bn" else "en"]
                    handoff_reason = "ai_answer_awaiting_review"
                elif getattr(res, "requires_grounding", False):
                    # Transactional intent the records could not ground: the
                    # grounder's authored hand-off line and its reason.
                    reply = result.get("bn") if lang == "bn" else result.get("en")
                    handoff_reason = result.get("reason") or "no_grounding_record"
                else:
                    # The classifier was not confident: its own authored line
                    # (disambiguation or transfer), never an invented answer.
                    reply = res.response_text_bn if lang == "bn" else res.response_text_en
                    handoff_reason = res.handoff_reason
                self.env["fix.conversation.turn"].create(
                    {
                        "conversation_id": conv.id,
                        "sequence": seq + 10,
                        "speaker": "ai",
                        "text": reply or self._HOLD_REPLY["bn" if lang == "bn" else "en"],
                        "lang": lang,
                    }
                )
                if sendable:
                    ask_row._guarded().write(
                        {"sent_at": fields.Datetime.now(), "sent_by": self.env.user.id}
                    )
                    conv.action_resolve(by_ai=True)
                else:
                    # T07: an unresolved turn always hands off - never a dead end
                    conv.action_handoff_to_agent(reason=handoff_reason or "escalation")

    # --- M32 grounding: transactional answers from live ERP records -----------------

    def _ground_intent_response(self, intent: str, text: str) -> dict:
        """Answer a transactional intent from the customer's real records.

        Returns {"bn", "en", "grounded", "reason"}. ``grounded`` is True only
        when the reply states facts read from records; otherwise the reply is
        guidance and ``reason`` is the handoff reason. Nothing here claims an
        action (booking, invoice dispatch) that was not performed."""
        self.ensure_one()
        handlers = {
            "order.status": self._ground_order_status,
            "repair.price_estimate": self._ground_price_estimate,
            "branch.locator": self._ground_branch_locator,
            "appointment.book": self._ground_appointment_book,
            "invoice.download": self._ground_invoice_download,
        }
        handler = handlers.get(intent)
        if not handler:
            return _answer(
                "আপনার প্রশ্নের নির্ভুল উত্তরের জন্য একজন কাস্টমার কেয়ার প্রতিনিধির সাথে যুক্ত করছি।",
                "Connecting you with a customer care specialist to assist you accurately.",
                False,
                "no_grounding_source",
            )
        try:
            return handler(text)
        except AccessError:
            return _answer(
                "আপনার তথ্য যাচাই করতে একজন কাস্টমার কেয়ার প্রতিনিধির সাথে যুক্ত করছি।",
                "Connecting you with a customer care representative to check your records.",
                False,
                "grounding_access_denied",
            )

    def _ground_order_status(self, text: str) -> dict:
        if "fix.service.order" not in self.env:
            return _answer(
                "অর্ডারের অবস্থা জানাতে একজন প্রতিনিধির সাথে যুক্ত করছি।",
                "Connecting you with a representative to check your order status.",
                False,
                "order_source_unavailable",
            )
        if not self.customer_id:
            # An unidentified contact never gets anyone's order status: the
            # agent verifies identity against the order reference.
            return _answer(
                "আপনার পরিচয় যাচাই করা যায়নি। অনুগ্রহ করে আপনার সার্ভিস অর্ডার নম্বরটি প্রস্তুত রাখুন, "
                "একজন প্রতিনিধি আপনার সাথে যুক্ত হচ্ছেন।",
                "We could not identify your account. Please keep your service order reference "
                "ready; connecting you with a representative.",
                False,
                "order_reference_required",
            )
        orders = self.env["fix.service.order"].search(
            [("customer_id", "=", self.customer_id.id)], order="create_date desc, id desc"
        )
        if not orders:
            return _answer(
                "আপনার নামে কোনো সার্ভিস অর্ডার পাওয়া যায়নি। একজন প্রতিনিধির সাথে যুক্ত করছি।",
                "We found no service order under your account. Connecting you with a "
                "representative.",
                False,
                "no_order_found",
            )
        lowered = (text or "").lower()
        # The order the customer names (by reference), else their latest one.
        order = next((o for o in orders if o.name and o.name.lower() in lowered), orders[0])
        state_bn, state_en = ORDER_STATE_TEXT.get(
            order.state, (order.state or "অজানা", order.state or "unknown")
        )
        device = order.device_id.display_name or ""
        suffix = " (%s)" % device if device else ""
        return _answer(
            "আপনার সার্ভিস অর্ডার %s%s: %s।" % (order.name, suffix, state_bn),
            "Your service order %s%s: %s." % (order.name, suffix, state_en),
            True,
        )

    def _ground_price_estimate(self, text: str) -> dict:
        """Quote a standard (tier-0, non-contract, in-validity) rate-card line
        only when the utterance names exactly one priced catalogue product;
        otherwise an agent confirms the price."""
        agent_confirms = _answer(
            "সঠিক খরচ ডিভাইস ও সমস্যার উপর নির্ভর করে — একজন প্রতিনিধি আপনাকে খরচ নিশ্চিত করবেন।",
            "The exact cost depends on the device and fault — a representative will confirm "
            "the price for you.",
            False,
            "price_requires_agent",
        )
        if "fix.rate.card" not in self.env or "product.product" not in self.env:
            return agent_confirms
        today = fields.Date.context_today(self)
        # A04 audit (2026-11-04): only a released (maker-checked) rate-card line
        # is a price; a draft or retired line is never quoted to a customer.
        cards = self.env["fix.rate.card"].search(
            [
                ("state", "=", "released"),
                ("min_tier", "=", 0),
                ("contract_no", "=", False),
                "|",
                ("valid_from", "=", False),
                ("valid_from", "<=", today),
                "|",
                ("valid_to", "=", False),
                ("valid_to", ">=", today),
            ]
        )
        if not cards:
            return agent_confirms
        products = self.env["product.product"].search(
            [("default_code", "in", cards.mapped("product_code"))]
        )
        has_bn = "name_bn" in products._fields
        norm = normalize_text(text)
        matches = products.browse()
        for product in products:
            names = [product.name, product.name_bn if has_bn else ""]
            if any(normalize_text(n or "") and normalize_text(n) in norm for n in names):
                matches |= product
        if len(matches) != 1:
            return agent_confirms
        card = cards.filtered(lambda c: c.product_code == matches.default_code)[:1]
        name_bn = (matches.name_bn if has_bn else "") or matches.name
        return _answer(
            "%s এর স্ট্যান্ডার্ড রেট: %.2f টাকা (ভ্যাট ব্যতীত)। চূড়ান্ত খরচ ডায়াগনস্টিকের পর নিশ্চিত করা হবে।"
            % (name_bn, card.unit_price),
            "Standard rate for %s: BDT %.2f (VAT-exclusive). The final cost is confirmed "
            "after diagnosis." % (matches.name, card.unit_price),
            True,
        )

    def _ground_branch_locator(self, text: str) -> dict:
        """Answer from the fix.branch record the customer names (branch name or
        its upazila); several or no matches go to an agent."""
        ask_agent = _answer(
            "কোন এলাকার শাখা জানতে চান তা নিশ্চিত করতে একজন প্রতিনিধির সাথে যুক্ত করছি।",
            "Connecting you with a representative to confirm which branch you are looking for.",
            False,
            "branch_not_identified",
        )
        if "fix.branch" not in self.env:
            return ask_agent
        tokens = set(normalize_text(text).split())
        matched = self.env["fix.branch"]
        for branch in self.env["fix.branch"].search([]):
            keys = set()
            for label in (
                branch.name,
                branch.name_bn,
                branch.address_id.upazila,
                branch.address_id.upazila_bn,
            ):
                keys |= set(normalize_text(label or "").split())
            keys -= _BRANCH_GENERIC_WORDS
            if any(len(k) >= 3 and k in tokens for k in keys):
                matched |= branch
        if len(matched) != 1:
            return ask_agent
        addr = matched.address_id
        addr_en = ", ".join(
            p for p in (addr.house, addr.street, addr.upazila, addr.district, addr.postcode) if p
        )
        addr_bn = addr.display_name if addr else ""
        if not (addr_en or matched.phone):
            return ask_agent
        phone_bn = " ফোন: %s।" % matched.phone if matched.phone else ""
        phone_en = " Phone: %s." % matched.phone if matched.phone else ""
        return _answer(
            "%s: %s।%s" % (matched.name_bn or matched.name, addr_bn or "ঠিকানা নথিভুক্ত নেই", phone_bn),
            "%s: %s.%s" % (matched.name, addr_en or "address not on record", phone_en),
            True,
        )

    def _ground_appointment_book(self, text: str) -> dict:
        # The assistant performs no booking: it must not say one was made.
        return _answer(
            "টেকনিশিয়ান ভিজিটের সময় নির্ধারণ করতে একজন প্রতিনিধির সাথে যুক্ত করছি। "
            "বুকিং নিশ্চিত হলে আপনাকে জানানো হবে।",
            "Connecting you with a representative to schedule the technician visit. "
            "You will be told once the booking is confirmed.",
            False,
            "appointment_requires_agent",
        )

    def _ground_invoice_download(self, text: str) -> dict:
        # Nothing is sent from here: guidance plus an agent, never "dispatched".
        return _answer(
            "আপনার ইনভয়েস ও মুশক ৬.৩ চালান কাস্টমার পোর্টালের ইনভয়েস অংশ থেকে ডাউনলোড করা যায়। "
            "কপি পাঠাতে একজন প্রতিনিধির সাথে যুক্ত করছি।",
            "Your invoices and Mushak 6.3 copies can be downloaded from the Invoices section "
            "of the customer portal. Connecting you with a representative to send a copy.",
            False,
            "invoice_requires_agent",
        )

    def mask_pii_for_mining(self) -> bool:
        """SC-003 DPIA requirement: Masks customer PII prior to offline mining."""
        import re

        for conv in self:
            for turn in conv.turn_ids:
                masked = re.sub(r"(\+?880?|0)1[3-9]\d{8}", "[PHONE_MASKED]", turn.text)
                masked = re.sub(
                    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL_MASKED]", masked
                )
                masked = re.sub(r"\b\d{10}\b|\b\d{17}\b", "[NID_MASKED]", masked)
                turn.write({"text": masked})
            conv.write({"pii_masked": True})
        return True


class FixConversationTurn(models.Model):
    """One turn in the transcript — who spoke, what was said, in which
    language. Transcript storage is the system of record (T04)."""

    _name = "fix.conversation.turn"
    _description = "Conversation Turn"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "conversation_id, sequence, id"

    conversation_id = fields.Many2one(
        "fix.conversation", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=10)
    speaker = fields.Selection(
        [("customer", "Customer"), ("ai", "AI Assistant"), ("agent", "Agent")], required=True
    )
    text = fields.Text(required=True)
    lang = fields.Selection([("bn", "বাংলা"), ("en", "English")], default="bn")
    spoken_at = fields.Datetime(default=fields.Datetime.now, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("text"):
                vals["text"] = scrub_pii(vals["text"])
        return super().create(vals_list)


class FixAssistantIntent(models.Model):
    """CD-M32-02: the TRANSACTIONAL intent register (T06: transactional
    only — the M61 knowledge base is W6, an already-ratified scope cut).
    T08: Bengali utterances are authored, never machine-translated."""

    _name = "fix.assistant.intent"
    _description = "Assistant Intent (transactional)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint("UNIQUE (code)", "Intent code must be unique")

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(
        required=True, size=32, help="e.g. order.status, invoice.download, appointment.book"
    )
    name = fields.Char(required=True)
    name_bn = fields.Char(
        string="Name (Bengali)",
        required=True,
        help="DE-17 + T08: authored Bengali, never machine-translated",
    )
    description = fields.Text()
    sample_bn = fields.Text(
        string="Bengali Utterances",
        required=True,
        help="Real Bengali utterances, one per line — the NLU test corpus (T08)",
    )
    sample_en = fields.Text(string="English Utterances")
    grounding = fields.Char(
        string="Grounding (live ERP data)",
        help="CD-M32-03: the live source this intent answers from — e.g. "
        "fix.service.order.tracking_ref via the party",
    )
    handoff_on_failure = fields.Boolean(
        default=True,
        help="T07: an intent the assistant cannot resolve hands off with full "
        "context rather than dead-ending",
    )
    active = fields.Boolean(default=True)
